<template>
  <el-container>
    <el-aside>
      <el-card class="box-card" style="margin: 10px;">
        <div slot="header">
          <span>{{contest.name}}</span>
        </div>
        <el-row class="carditem">
          <el-tag>{{'学科: '+contest.subject}}</el-tag>
        </el-row>
        <el-row class="carditem">
          <el-tag>{{'队伍人数: '+contest.groupSize}}</el-tag>
        </el-row>
        <el-row class="carditem">
          <el-tag>{{'举办方: '+contest.publisher}}</el-tag>
        </el-row>
      </el-card>
      <el-card style="margin: 10px;">
        <el-menu :default-active="activeIndex" class="el-menu-vertical-demo" style="border: none;">
          <el-menu-item
            v-for="(item,index) in sidebarList"
            :key="index"
            :index="index.toString()"
            @click="pushRoute(item.name)"
          >{{ item.label }}</el-menu-item>
        </el-menu>
      </el-card>
    </el-aside>
    <el-main style="height:auto;">
      <transition name="component-fade" mode="out-in">
        <router-view :contest="contest" :contestId="contestId" @refreshContest="refreshContest"></router-view>
      </transition>
    </el-main>
  </el-container>
</template>

<script>
export default {
  name: 'ControlPanel',
  created() {
    this.refreshContest()
  },
  data() {
    return {
      contest: {
        name: '比赛名称',
        subject: '比赛学科',
        groupSize: '队伍人数',
        publisher: '举办方',
        procedure: [],
        id: -1,
        enrollStart: '',
        enrollEnd: '',
        imgUrl: '',
        enrollUrl: '',
        charge: 0,
        upvote: 0,
        downvote: 0,
        stage: 0,
        detail: ''
      },
      sidebarList: [
        {
          name: 'overview',
          label: '比赛总览'
        },
        {
          name: 'managegroup',
          label: '管理报名队伍'
        },
        {
          name: 'managejudge',
          label: '管理评委'
        },
        {
          name: 'managesubmission',
          label: '管理提交'
        },
        {
          name: 'managereview',
          label: '管理批阅'
        },
        {
          name: 'notices',
          label: '管理公告'
        },
        {
          name: 'groupinfo',
          label: '选手信息'
        }
      ]
    }
  },
  methods: {
    refreshContest() {
      this.$http
        .get(`/api/contests/${this.contestId}`)
        .then(resp => {
          if (resp.body.code !== 0) {
            throw new Error(resp.body.error)
          }
          this.contest = resp.body.data
        })
        .catch(err => {
          this.$alert(err.toString())
        })
    },
    pushRoute(name) {
      this.$router.push({
        name,
        params: {
          id: this.contestId
        }
      })
    }
  },
  computed: {
    contestId() {
      return parseInt(this.$route.params.id)
    },
    activeIndex() {
      let name = this.$route.name
      for (let i = 0; i < this.sidebarList.length; i++) {
        if (name === this.sidebarList[i].name) {
          return i.toString()
        }
      }
      return '0'
    }
  }
}
</script>
<style scoped>
.el-tag {
  width: auto;
  margin: 5px;
}

.component-fade-enter-active,
.component-fade-leave-active {
  transition: opacity 0.3s ease;
}
.component-fade-enter, .component-fade-leave-to
/* .component-fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
