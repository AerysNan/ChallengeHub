<template>
  <el-card :body-style="{ padding: '0px' }" class="single-card">
    <el-row style="margin: 0px;">
      <el-col :span="4">
        <img :src="contest.imgUrl" class="judged-contest-card" :onerror="defaultImg">
      </el-col>

      <el-col :span="12" style="text-align: left; padding-left: 20px;">
        <div class="contest-name">{{ contest.name }}</div>
        <div class="contest-info">
          <el-button
            type="text"
            @click="$router.push(`/profile/${contest.publisher}`)"
            style="padding: 0; font-size: 16px;"
          >{{ contest.publisher }}</el-button>
        </div>
        <div class="contest-info">比赛已结束于 {{ endingDeadline }}</div>
        <el-button type="text" @click="$router.push(`/contest/detail/${contest.id}`)">比赛详情</el-button>
        <el-button type="text" @click="$router.push(`/contest/notice/${contest.id}`)">比赛公告</el-button>
      </el-col>

      <el-col :span="8" style="text-align: right; padding-right: 20px;">
        <div class="right-header">评审已完成</div>
        <div class="right-info">你已完成 {{ task.done }} 项评审任务</div>
        <div style="margin-top: 20px;">
          <el-button type="primary" @click="gotoWorkspace()">查看评审详情</el-button>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script>
import { isoToHumanReadable } from '@/lib/util.js'

export default {
  name: 'JudgedContestFinished',
  data() {
    return {
      defaultImg: 'this.src="' + require('@/assets/placeholder.png') + '"'
    }
  },
  computed: {
    endingDeadline: function() {
      let procedure = this.contest.procedure
      let deadline = procedure[procedure.length - 1].endTime
      return isoToHumanReadable(deadline)
    }
  },
  props: ['contest', 'task'],
  methods: {
    gotoWorkspace() {
      this.$router.push(`/judge/workspace/${this.contest.id}`)
    }
  }
}
</script>

<style scoped>
.single-card {
  height: 150px;
  margin-left: 10px;
  margin-right: 10px;
}

.judged-contest-card {
  max-width: 200px;
  max-height: 152px;
  width: auto;
  height: auto;
}

.contest-name {
  margin-top: 10px;
  font-weight: bold;
  font-size: 32px;
  white-space: nowrap;
  overflow: auto;
}

.contest-name::-webkit-scrollbar {
  display: none;
}

.contest-info {
  margin-top: 5px;
  color: grey;
}

.right-header {
  margin-top: 10px;
  font-weight: bold;
  font-size: 24px;
}

.right-info {
  margin-top: 5px;
  color: gray;
}
</style>
