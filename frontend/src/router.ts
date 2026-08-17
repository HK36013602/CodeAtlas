import { createRouter,createWebHistory } from 'vue-router'
export const router=createRouter({history:createWebHistory(),routes:[
 {path:'/',redirect:'/map'},
 {path:'/map',name:'map',meta:{title:'架构图谱'},component:()=>import('./views/MapView.vue')},
 {path:'/risks',name:'risks',meta:{title:'风险诊断'},component:()=>import('./views/RisksView.vue')},
 {path:'/files',name:'files',meta:{title:'热点文件'},component:()=>import('./views/FilesView.vue')},
 {path:'/repository',name:'repository',meta:{title:'代码接入'},component:()=>import('./views/RepositoryView.vue')},
 {path:'/:pathMatch(.*)*',redirect:'/map'}
],scrollBehavior:()=>({top:0})})
