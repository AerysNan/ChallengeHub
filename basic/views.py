from django.db import transaction
from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone
from basic.models import Competition, Group, CStage, GStage, ReviewMeta, Notice, Vote
from useraction.models import User
from match.models import Invitation
from typing import Dict, Any, Callable, List
from ChallengeHub.utils import BaseView as View, require_logged_in, make_errors, require_to_be_organization, require_to_be_individual, require_to_be_publisher
from ChallengeHub.settings import MONGO_CLIENT, BASE_DIR
import os
import json


class ContestCollectionView(View):
    def get(self, request) -> Any:
        competitions = Competition.objects.all()
        if 'search' in request.data:
            competitions = competitions.filter(
                name__icontains=request.data.get('search'))
        if 'sortBy' in request.data:
            if request.data['sortBy'] == 'numVotes':
                competitions = competitions.order_by('-upvote')
        return [competition.to_dict() for competition in competitions]

    @require_logged_in
    @require_to_be_organization
    def post(self, request) -> Any:
        self.check_input([
            'name', 'subject', 'groupSize', 'enrollStart', 'enrollEnd',
            'detail', 'procedure', 'enrollUrl', 'charge', 'enrollForm', 'imgUrl',
        ])
        c = Competition(
            name=request.data.get('name'),
            subject=request.data.get('subject'),
            group_size=request.data.get('groupSize'),
            enroll_start=request.data.get('enrollStart'),
            enroll_end=request.data.get('enrollEnd'),
            detail=request.data.get('detail'),
            enroll_url=request.data.get('enrollUrl'),
            charge=request.data.get('charge'),
            img_url=request.data.get('imgUrl'),
            publisher=request.user
        )
        c.save()
        procedure = request.data.get('procedure')
        for (i, prod) in enumerate(procedure):
            stage = CStage(name=prod["name"], start_time=prod["startTime"],
                           end_time=prod["endTime"], stage=2 * i + 1, competition=c)
            stage.save()
        collection = MONGO_CLIENT.competition.enrollForm
        collection.insert_one(
            {'id': c.id, 'enrollForm': request.data.get('enrollForm')})
        if (not c.enroll_url):
            c.enroll_url = '/contest/enroll/{}'.format(c.id)
            c.save()
        return c.to_dict()


class ContestDetailView(View):
    def get(self, request, contest_id: str) -> Any:
        c = Competition.objects.get(id=int(contest_id))
        info = c.to_dict(detail=True)
        info['userRelated'] = {}
        if request.user.is_authenticated():
            vote = request.user.user_votes.filter(competition=c).first()
            info['userRelated']['upvoteStatus'] = vote.status if vote else 0
        else:
            info['userRelated']['upvoteStatus'] = 0
        return info

    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def post(self, request, contest_id: str) -> Any:
        self.check_input(['stage'])
        competition = Competition.objects.get(id=int(contest_id))
        stage = int(request.data.get('stage'))

        if stage > 0 and stage % 2 == 0:  # when enter judge stage, update all qualified group to that stage
            qualified_groups = Group.objects.filter(
                current_stage=competition.current_stage, competition=competition)
            qualified_groups.update(current_stage=stage)

        competition.current_stage = stage
        competition.save()
        return


class TaskStatView(View):
    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def get(self, request, contest_id: str) -> Any:
        self.check_input(['stage'])
        c = Competition.objects.get(id=int(contest_id))
        stage = int(request.data['stage'])
        cstage = c.stage_list.get(stage=stage if stage % 2 == 1 else stage - 1)
        qualified_groups = c.enrolled_groups.filter(current_stage=stage)
        submitted_groups = 0
        total_tasks = 0
        reviewed_tasks = 0
        for group in qualified_groups:
            gstage = group.stage_list.get(
                stage=stage if stage % 2 == 1 else stage - 1)
            if gstage.has_commit:
                submitted_groups += 1
            review_metas = gstage.review_meta_list.all()
            total_tasks += len(review_metas)
            for task in review_metas:
                if task.reviewed:
                    reviewed_tasks += 1
        return {
            "totalTasks": total_tasks,
            "reviewedTasks": reviewed_tasks,
            "qualifiedGroups": len(qualified_groups),
            "submittedGroups": submitted_groups,
            "isAssigned": cstage.is_assigned
        }


class ContestReviewTaskView(View):
    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def get(self, request, contest_id: str) -> Any:
        self.check_input(['stage'])
        stage = int(request.data['stage'])
        c = Competition.objects.get(id=int(contest_id))
        data = []
        for judge in c.judges.all():
            assigned = 0
            completed = 0
            for task in judge.review_list.all():
                gstage = task.stage
                if gstage.stage == stage - 1 and gstage.group.competition.id == int(contest_id):
                    assigned += 1
                    if task.reviewed:
                        completed += 1
            data.append({
                "username": judge.username,
                "email": judge.email,
                "assigned": assigned,
                "completed": completed
            })
        return data


class ContestAutoAssignView(View):
    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def post(self, request, contest_id: str) -> Any:
        self.check_input(['stage', 'serious', 'maxconn', 'judges'])
        c = Competition.objects.get(id=int(contest_id))
        stage = int(request.data['stage'])
        maxconn = request.data['maxconn']
        serious = request.data['serious']
        cstage = c.stage_list.get(stage=stage if stage % 2 == 1 else stage - 1)
        if cstage.is_assigned:
            raise Exception("already auto-assigned!")
        qualified_groups = c.enrolled_groups.filter(current_stage=stage)
        submitted_gstages = []
        for group in qualified_groups:
            gstage = group.stage_list.get(
                stage=stage if stage % 2 == 1 else stage - 1)
            if gstage.has_commit:
                submitted_gstages.append(gstage)
        judges = list(c.judges.all())

        judge_count = {x.username: 0 for x in judges}
        group_count = {x.id: 0 for x in submitted_gstages}

        if cstage.is_assigned and serious:
            raise Exception("already assigned")

        # assign assignment
        index = 0
        for gstage in submitted_gstages:
            for i in range(maxconn):
                judge = judges[index % len(judges)]
                index += 1
                judge_count[judge.username] += 1
                group_count[gstage.id] += 1
                if serious:
                    review_meta = ReviewMeta(reviewer=judge, stage=gstage)
                    review_meta.save()
        if serious:
            cstage.is_assigned = True
            cstage.save()
        groupNotFull = len(
            [key for key, value in group_count.items() if value < maxconn])
        groupZero = len(
            [key for key, value in group_count.items() if value == 0])
        return {
            "judges": [
                {"username": judge.username, "assign": judge_count[judge.username]} for judge in judges
            ],
            "groupNotFull": groupNotFull,
            "groupZero": groupZero
        }


class ContestReviewerView(View):
    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def post(self, request, contest_id: str) -> Any:
        self.check_input(['username'])
        c = Competition.objects.get(id=int(contest_id))
        with transaction.atomic():
            for username in request.data['username']:
                user = User.objects.get(username=username)
                c.judges.add(user)
            c.save()
        return

    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def get(self, request, contest_id: str) -> Any:
        c = Competition.objects.get(id=int(contest_id))
        judges = c.judges.all()
        data = [judge.to_dict() for judge in judges]
        return data


class ContestVoteView(View):
    def post(self, request, contest_id: str) -> Any:
        self.check_input(['upvote'])
        c = Competition.objects.get(id=int(contest_id))
        vote = Vote.vote(c, request.user, request.data['upvote'])
        return {
            'upvote': c.upvote,
            'downvote': c.downvote,
            'upvoteStatus': vote.status,
        }


class GroupStageView(View):
    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def post(self, request, contest_id: str) -> Any:
        self.check_input(['group_ids', 'stage'])
        stage = int(request.data['stage'])
        with transaction.atomic():
            for id in request.data['group_ids']:
                group = Group.objects.get(id=id)
                group.current_stage = stage
                group.save()
                if group.stage_list.filter(stage=stage):
                    raise Exception(
                        f"stage {stage} already exists for group {group.name}")
                gstage = GStage(stage=stage, group=group, score=0.0)
                gstage.save()
        return

    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def get(self, request, contest_id: str) -> Any:
        c = Competition.objects.get(id=int(contest_id))
        groups = c.enrolled_groups.all()
        data = [group.to_dict() for group in groups]
        return data


class GroupDetailView(View):
    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def get(self, request, contest_id: str) -> Any:
        data = {}
        competition = Competition.objects.get(id=int(contest_id))
        collection = MONGO_CLIENT.competition.enrollForm
        data['enrollForm'] = collection.find_one({'id': int(contest_id)})['enrollForm']
        groups = competition.enrolled_groups.all()
        data['info'] = [{
            'name': group.name,
            'form': MONGO_CLIENT.group.enrollForm.find_one({'id': int(group.id)})['enrollForm']
        } for group in groups]
        return data


class ContestEnrollView(View):
    def get(self, request, contest_id: str) -> Any:
        collection = MONGO_CLIENT.competition.enrollForm
        data = collection.find_one({'id': int(contest_id)})
        return {'enrollForm': data['enrollForm']}

    @require_logged_in
    @require_to_be_individual
    def post(self, request, contest_id: str) -> Any:
        self.check_input(['name', 'leaderName', 'members', 'form'])
        leader = User.objects.get(username=request.data.get('leaderName'))
        if leader.joint_groups.all():
            raise Exception(f"you are already in group {leader.joint_groups.first().name}")
        group = Group(
            name=request.data.get('name'),
            competition=Competition.objects.get(id=int(contest_id)),
            leader=leader
        )
        group.save()
        # save first to have an ``id``
        group.members.add(group.leader)
        group.save()
        stage = GStage(stage=1, score=0, group=group)
        stage.save()

        collection = MONGO_CLIENT.group.enrollForm
        collection.insert_one(
            {'id': group.id, 'enrollForm': request.data['form']})
        members = request.data['members']
        for member in members:
            if member == request.data.get('leaderName'):
                continue
            user = User.objects.get(username=member)
            message = Invitation(group=group, invitee=user)
            message.save()
        return {'id': group.id}


class ContestSubmissionView(View):
    @require_logged_in
    @require_to_be_individual
    def post(self, request, contest_id: str) -> Any:
        user = request.user
        group = user.joint_groups.get(competition__id=int(contest_id))
        submit = request.data.get('file')
        stage = group.current_stage
        if (stage != group.competition.current_stage or stage % 2 != 1):
            raise Exception('no authority to submit now')
        _, extension = os.path.splitext(submit.name)

        commit_dir = os.path.join('contest',
                                  contest_id, str(stage))
        commit_path = os.path.join(commit_dir, f'{group.id}{extension}')
        abs_dir = os.path.join(BASE_DIR, 'submit', commit_dir)
        abs_path = os.path.join(BASE_DIR, 'submit', commit_path)
        if (not os.path.exists(abs_dir)):
            os.makedirs(abs_dir)
        with open(abs_path, 'wb+') as f:
            for chunk in submit.chunks():
                f.write(chunk)
        group_stage = group.stage_list.get(stage=stage)
        group_stage.commit_path = os.path.join('/static', commit_path)
        group_stage.submission = request.data.get('submissionName')
        group_stage.has_commit = True
        group_stage.save()
        return

    @require_logged_in
    @require_to_be_individual
    def get(self, request, contest_id: str) -> Any:
        user = request.user
        group = user.joint_groups.get(competition__id=int(contest_id))
        stage = request.data.get('stage', group.current_stage)
        stage = int(stage)
        if stage < 1:
            raise Exception('invalid stage')
        if stage % 2 == 0:
            stage = stage - 1
        group_stage = group.stage_list.get(stage=stage)
        if not group_stage.has_commit:
            raise Exception('not committed yet')
        return {
            'score': group_stage.score,
            'reviews': [{'rating': x.score, 'msg': x.msg} for x in group_stage.review_meta_list.all()],
            'submissionName': group_stage.submission,
            'url': group_stage.commit_path
        }


class UserCollectionView(View):
    @require_logged_in
    def get(self, request) -> Any:
        users = User.objects.all()
        if 'prefix' in request.data:
            users = users.filter(
                username__startswith=request.data.get('prefix'))
        return [{'username': user.username} for user in users]


class UserCreatedView(View):
    @require_logged_in
    @require_to_be_organization
    def get(self, request) -> Any:
        user = request.user
        competitions = user.published_competitions.all()
        return [competition.to_dict() for competition in competitions]


class UserJudgedView(View):
    @require_logged_in
    @require_to_be_individual
    def get(self, request) -> Any:
        user = request.user
        competitions = [
            r.stage.group.competition for r in user.review_list.all()]
        data = []
        for competition in competitions:
            stage = competition.current_stage
            stage = stage if stage % 2 == 1 else stage - 1
            reviews = user.review_list.filter(
                stage__group__competition=competition, stage__stage=stage)
            data.append({
                'contest': competition.to_dict(),
                'task': {
                    'count': reviews.count(),
                    'done': reviews.filter(reviewed=True).count()
                }
            })
        return data


class UserEnrolledView(View):
    @require_logged_in
    @require_to_be_individual
    def get(self, request) -> Any:
        user = request.user
        return [{
            'group': group.to_dict(),
            'contest': group.competition.to_dict()
        } for group in user.joint_groups.all()]


class JudgeReviewView(View):
    @require_logged_in
    @require_to_be_individual
    def get(self, request, contest_id: str) -> Any:
        def get_extension(pathname: str) -> str:
            _, extension = os.path.splitext(pathname)
            while len(extension) >= 1 and extension[0] == '.':
                extension = extension[1:]
            return extension

        competition = Competition.objects.get(id=int(contest_id))
        stage = request.data.get('stage', competition.current_stage)
        stage = int(stage)
        if stage == -1:
            # contest ended
            return {'contest': competition.to_dict(), 'task': None, 'submissions': []}
        stage = stage if stage % 2 == 1 else stage - 1
        data = {}
        data['contest'] = competition.to_dict()
        data['contest']['standard'] = competition.stage_list.get(
            stage=stage).criterion
        reviews = request.user.review_list.filter(
            stage__group__competition=competition, stage__stage=stage)
        data['task'] = {
            'count': reviews.count(),
            'done': reviews.filter(reviewed=True).count()
        }
        data['submissions'] = [{
            'id': review.id,
            'submissionName': review.stage.submission,
            'reviewed': review.reviewed,
            'rating': review.score,
            'url': review.stage.commit_path,
            'msg': review.msg,
            'extension': get_extension(review.stage.commit_path)} for review in reviews]
        return data

    @require_logged_in
    @require_to_be_individual
    def post(self, request, contest_id: str) -> Any:
        self.check_input(['reviews'])
        competition = Competition.objects.get(id=int(contest_id))
        reviews = request.data.get('reviews')
        for r in reviews:
            meta = ReviewMeta.objects.get(id=r['id'])
            meta.reviewed = meta.reviewed or r['reviewed']
            meta.score = r['rating']
            meta.msg = r.get('msg', '')
            meta.save()
            reviews = meta.stage.review_meta_list.all()
            sum = 0.0
            for x in reviews:
                sum += x.score
            meta.stage.score = sum / reviews.count()
            meta.stage.save()
        return


class CriterionView(View):
    @require_logged_in
    def get(self, request, contest_id: str) -> Any:
        self.check_input(['stage'])
        contest_id = int(contest_id)
        stage = int(request.data['stage'])
        if stage % 2 == 0:
            stage -= 1
        contest = Competition.objects.get(id=contest_id)
        cstage = CStage.objects.get(stage=stage, competition=contest)
        return {'criterion': cstage.criterion}

    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def post(self, request, contest_id: str) -> Any:
        self.check_input([
            'stage', 'criterion'
        ])
        contest_id = int(contest_id)
        contest = Competition.objects.get(id=contest_id)
        stage = int(request.data['stage'])
        if stage % 2 == 0:
            stage -= 1
        criterion = request.data['criterion']
        cstage = CStage.objects.get(stage=stage, competition=contest)
        cstage.criterion = criterion
        cstage.save()
        return


class SubmissionAllView(View):
    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def get(self, request, contest_id: str) -> Any:
        self.check_input(['stage'])
        contest_id = int(contest_id)
        stage = int(request.data['stage'])
        if stage % 2 == 0:
            stage -= 1
        contest = Competition.objects.get(id=contest_id)
        submissions = GStage.objects.filter(
            stage=stage, group__competition=contest)
        res = []
        for submission in submissions:
            if submission.has_commit:
                obj = {}
                obj['teamName'] = submission.group.name
                obj['name'] = submission.submission
                obj['downloadUrl'] = submission.commit_path
                obj['score'] = submission.score
                judges = []
                review_set = ReviewMeta.objects.filter(stage=submission)
                for review in review_set:
                    judges.append({
                        'username': review.reviewer.username,
                        'hasReviewed': review.reviewed,
                        'score': review.score,
                        'msg': review.msg,
                    })
                obj['judges'] = judges
                res.append(obj)
        return res


class NoticeCollectionView(View):
    def get(self, request, contest_id: str) -> Any:
        competition = Competition.objects.get(id=int(contest_id))
        return {
            'notices': [notice.to_dict() for notice in Notice.objects.filter(competition=competition)],
            'contest': competition.to_dict(),
        }

    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def post(self, request, contest_id: str) -> Any:
        competition = Competition.objects.get(id=int(contest_id))
        self.check_input(['title', 'content'])
        notice = Notice(
            competition=competition,
            title=request.data.get('title'),
            modified_time=timezone.now(),
            content=request.data.get('content'),
        )
        notice.save()
        return


class NoticeDetailView(View):
    def get(self, request, contest_id: str, notice_id: str) -> Any:
        notice = Notice.objects.get(id=int(notice_id))
        return notice.to_dict(detail=True)

    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def delete(self, request, contest_id: str, notice_id: str) -> Any:
        competition = Competition.objects.get(id=int(contest_id))
        notice = Notice.objects.get(id=int(notice_id))
        notice.delete()
        return

    @require_logged_in
    @require_to_be_organization
    @require_to_be_publisher
    def put(self, request, contest_id: str, notice_id: str) -> Any:
        competition = Competition.objects.get(id=int(contest_id))
        notice = Notice.objects.get(id=int(notice_id))
        self.check_input(['title', 'content'])
        notice.title = request.data.get('title')
        notice.content = request.data.get('content')
        notice.modified_time = timezone.now()
        notice.save()
        return

        
class UserProfileView(View):
    def get(self, request, username) -> Any:
        user = User.objects.get(username=username)
        return user.to_dict()