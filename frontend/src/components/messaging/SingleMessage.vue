<template>
  <el-card
    style="text-align: left; margin-left: 10px; margin-right: 10px;"
    body-style="padding: 10px;"
  >
    <div v-if="message.type === 'letter'">
      <div class="title">
        <div>
          <span>来自</span>
          <span class="theme">
            <el-button
              type="text"
              @click="$router.push(`/profile/${message.sender}`)"
              style="padding: 0; font-size: 16px;"
            >{{message.sender}}</el-button>
          </span>
          <span>的消息</span>
        </div>
        <div class="send-date">
          <span>发送于 {{sendTime}}</span>
        </div>
      </div>
      <div class="content">{{message.content}}</div>
      <el-button
        v-if="!read"
        type="primary"
        plain
        @click="$emit('mark-as-read', {id: message.id, type: message.type})"
      >标记为已读</el-button>
      <el-button
        v-if="read"
        type="primary"
        plain
        @click="$emit('delete-message', {id: message.id, type: message.type})"
      >删除消息</el-button>
      <el-button type="primary" @click="$emit('reply-message', message.sender)">回复消息</el-button>
    </div>

    <div v-if="message.type === 'system'">
      <div class="title">
        <div>
          <span class="theme">系统通知</span>
        </div>
        <div class="send-date">
          <span>发送于 {{sendTime}}</span>
        </div>
      </div>
      <div class="content">{{message.content}}</div>
      <el-button
        v-if="!read"
        type="primary"
        plain
        @click="$emit('mark-as-read', {id: message.id, type: message.type})"
      >标记为已读</el-button>
      <el-button
        v-if="read"
        type="primary"
        plain
        @click="$emit('delete-message', {id: message.id, type: message.type})"
      >删除消息</el-button>
    </div>

    <div v-if="message.type === 'invitation'">
      <div class="title">
        <div>
          <span class="theme">比赛组队邀请</span>
        </div>
        <div class="send-date">
          <span>发送于 {{sendTime}}</span>
        </div>
      </div>
      <div class="content" style="text-align: center;">
        <el-card shadow="never" style="width: 600px; margin-left: auto; margin-right: auto;">
          <div>
            <span class="theme bold">
              <el-button
                type="text"
                @click="$router.push(`/profile/${message.content.leaderName}`)"
                style="padding: 0; font-size: 16px;"
              >{{message.content.leaderName}}</el-button>
            </span>
            <span style="margin-left: 5px; margin-right: 5px;">邀请你加入</span>
            <span class="theme bold">{{message.content.groupName}}</span>
            <span style="margin-left: 5px; margin-right: 5px;">参加比赛</span>
            <span class="theme bold">
              <el-button
                type="text"
                @click="$router.push(`/contest/detail/${message.content.contestId}`)"
                style="padding: 0; font-size: 16px;"
              >{{message.content.contestName}}</el-button>
            </span>
          </div>
          <div style="margin-top: 20px; color: gray; font-size: 12px; margin-bottom: 10px;">
            <span v-if="message.content.status === 0">在接收邀请后，组长确认组队前，你依然可以退出</span>
            <span v-if="message.content.status === 1">你已接受这次邀请</span>
            <span v-if="message.content.status === 2">你已拒绝这次邀请</span>
            <span v-if="message.content.status === 3">这个邀请已经过期或取消</span>
          </div>

          <el-button
            type="success"
            @click="$emit('accept-invitation', {contestId: message.content.contestId, groupId: message.content.groupId})"
            v-if="message.content.status === 0"
          >接受邀请</el-button>
          <el-button
            type="danger"
            @click="$emit('reject-invitation', {contestId: message.content.contestId, groupId: message.content.groupId})"
            v-if="message.content.status === 0"
          >拒绝邀请</el-button>
        </el-card>
      </div>
      <el-button
        v-if="!read"
        type="primary"
        plain
        @click="$emit('mark-as-read', {id: message.id, type: message.type})"
      >标记为已读</el-button>
      <el-button
        v-if="read"
        type="primary"
        plain
        @click="$emit('delete-message', {id: message.id, type: message.type})"
      >删除消息</el-button>
      <el-button
        type="primary"
        plain
        @click="$emit('reply-message', message.content.leaderName)"
      >向组长发消息</el-button>
    </div>

    <div v-if="message.type === 'reviewer_invitation'">
      <div class="title">
        <div>
          <span class="theme">比赛评审邀请</span>
        </div>

        <div class="send-data">
          <span>发送于 {{sendTime}}</span>
        </div>
      </div>

      <div class="content" style="text-align: center;">
        <el-card shadow="never" style="width: 600px; margin-left: auto; margin-right: auto;">
          <div>
            <span class="theme bold">
              <el-button
                type="text"
                @click="$router.push(`/contest/detail/${message.content.contestId}`)"
                style="padding: 0; font-size: 16px;"
              >{{message.content.contestName}}</el-button>
            </span>
            <span style="margin-left: 5px; margin-right: 5px;">的主办方</span>
            <span class="theme bold">
              <el-button
                type="text"
                @click="$router.push(`/profile/${message.sender}`)"
                style="padding: 0; font-size: 16px;"
              >{{message.sender}}</el-button>
            </span>
            <span style="margin-left: 5px; margin-right: 5px;">邀请你进行评审</span>
          </div>
          <div style="margin-top: 20px; color: gray; font-size: 12px; margin-bottom: 10px;">
            <span v-if="message.content.status === 0">请及时做出选择</span>
            <span v-if="message.content.status === 1">你已接受这次邀请</span>
            <span v-if="message.content.status === 2">你已拒绝这次邀请</span>
            <span v-if="message.content.status === 3">这个邀请已经过期或取消</span>
          </div>

          <el-button
            type="success"
            @click="$emit('accept-reviewer-invitation', {contestId: message.content.contestId})"
            v-if="message.content.status === 0"
          >接受邀请</el-button>
          <el-button
            type="danger"
            @click="$emit('reject-reviewer-invitation', {contestId: message.content.contestId})"
            v-if="message.content.status === 0"
          >拒绝邀请</el-button>
        </el-card>
      </div>
      <el-button
        v-if="!read"
        type="primary"
        plain
        @click="$emit('mark-as-read', {id: message.id, type: message.type})"
      >标记为已读</el-button>
      <el-button
        v-if="read"
        type="primary"
        plain
        @click="$emit('delete-message', {id: message.id, type: message.type})"
      >删除消息</el-button>
    </div>
  </el-card>
</template>

<script>
import { isoToHumanReadable } from '@/lib/util.js'

export default {
  props: ['message', 'read'],
  computed: {
    sendTime() {
      return isoToHumanReadable(this.message.sendTime)
    }
  }
}
</script>

<style scoped>
.content {
  margin-top: 15px;
  margin-left: 30px;
  margin-right: 30px;
  margin-bottom: 15px;
}

.send-date {
  font-size: 12px;
}

.title {
  color: gray;
}

.bold {
  font-weight: bold;
}

.theme {
  color: #409eff;
}
</style>
