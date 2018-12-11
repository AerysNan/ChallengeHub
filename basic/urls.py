from django.conf.urls import url
from basic import views

urlpatterns = [
    url(r'contests$',
        views.ContestCollectionView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)$',
        views.ContestDetailView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/enroll$',
        views.ContestEnrollView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/groups$',
        views.GroupStageView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/groups_detail$',
        views.GroupDetailView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/submissions$',
        views.ContestSubmissionView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/taskstat$',
        views.TaskStatView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/reviewer$',
        views.ContestReviewerView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/reviewtask$',
        views.ContestReviewTaskView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/auto_assign$',
        views.ContestAutoAssignView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/criterion$',
        views.CriterionView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/submission_all$',
        views.SubmissionAllView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/notices$',
        views.NoticeCollectionView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/vote$',
        views.ContestVoteView.as_view()),
    url(r'contests/(?P<contest_id>[0-9]+)/notices/(?P<notice_id>[0-9]+)$',
        views.NoticeDetailView.as_view()),
    url(r'users$',
        views.UserCollectionView.as_view()),
    url(r'users/enrolled$',
        views.UserEnrolledView.as_view()),
    url(r'users/judged$',
        views.UserJudgedView.as_view()),
    url(r'users/created$',
        views.UserCreatedView.as_view()),
    url(r'users/profile/(?P<username>.*)$',
        views.UserProfileView.as_view()),
    url(r'judges/(?P<contest_id>[0-9]+)$',
        views.JudgeReviewView.as_view()),
]
