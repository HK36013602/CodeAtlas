<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { PhArrowsClockwise, PhBlueprint, PhBracketsCurly, PhGitBranch, PhListMagnifyingGlass, PhPath, PhWarning, PhX } from '@phosphor-icons/vue';
import { getAnalysis, getScanStatus, startScan } from './api';
import DependencyGraph from './components/DependencyGraph.vue';
import type { Analysis } from './types';

const data=ref<Analysis>();const loading=ref(true);const error=ref('');const selectedId=ref('payment');const showCycles=ref(true);const scanning=ref(false);const mobilePanel=ref(false);
const selected=computed(()=>data.value?.nodes.find(n=>n.id===selectedId.value));
const related=computed(()=>data.value?.edges.filter(e=>e.source===selectedId.value||e.target===selectedId.value)||[]);
const selectedInsight=computed(()=>data.value?.insights.find(i=>i.module===selectedId.value));
async function load(){loading.value=true;error.value='';try{data.value=await getAnalysis()}catch(e){error.value=e instanceof Error?e.message:'加载失败'}finally{loading.value=false}}
const pause=(ms:number)=>new Promise(resolve=>setTimeout(resolve,ms));
async function scan(){scanning.value=true;error.value='';try{const queued=await startScan();for(let attempt=0;attempt<30;attempt+=1){await pause(400);const task=await getScanStatus(queued.task_id);if(task.status==='success'){await load();return}if(task.status==='failure')throw new Error(task.error||'扫描失败')}throw new Error('扫描仍在进行，请稍后刷新。')}catch(e){error.value=e instanceof Error?e.message:'扫描失败'}finally{scanning.value=false}}
function select(id:string){selectedId.value=id;mobilePanel.value=true}onMounted(load);
const fmt=(n:number)=>n>=1000?`${(n/1000).toFixed(1)}k`:String(n);
</script>

<template>
<div class="app-shell">
  <aside class="rail">
    <a class="brand" href="#top" aria-label="CodeAtlas 首页"><PhBlueprint :size="25" weight="duotone"/><span>CodeAtlas</span></a>
    <nav aria-label="主要导航">
      <a class="active" href="#map"><PhGitBranch :size="19"/><span>架构图谱</span></a>
      <a href="#risks"><PhWarning :size="19"/><span>风险诊断</span></a>
      <a href="#files"><PhListMagnifyingGlass :size="19"/><span>热点文件</span></a>
    </nav>
    <div class="rail-foot"><span class="status-dot"></span><span>分析引擎在线</span></div>
  </aside>
  <main id="top">
    <header class="topbar">
      <div v-if="data" class="repo-meta"><strong>{{data.repository.name}}</strong><span>{{data.repository.branch}}</span><code>{{data.repository.commit}}</code><em>模拟仓库</em></div>
      <div v-else class="repo-meta skeleton-line"></div>
      <button class="scan-button" :disabled="scanning||loading" @click="scan"><PhArrowsClockwise :class="{spinning:scanning}" :size="17"/>{{scanning?'正在扫描':'重新扫描'}}</button>
    </header>
    <div v-if="error" class="error-banner" role="alert"><span>{{error}}</span><button @click="load">重试</button></div>
    <template v-if="loading">
      <section class="loading-layout" aria-label="正在加载"><div class="skeleton graph-skeleton"></div><div class="skeleton panel-skeleton"></div></section>
    </template>
    <template v-else-if="data">
      <section class="summary-strip" aria-label="仓库摘要">
        <div><span>模块</span><strong>{{data.summary.modules}}</strong></div><div><span>依赖</span><strong>{{data.summary.dependencies}}</strong></div><div><span>代码行</span><strong>{{fmt(data.summary.lines)}}</strong></div><div><span>循环</span><strong class="warning-value">{{data.summary.cycles}}</strong></div><div><span>平均复杂度</span><strong>{{data.summary.avg_complexity}}</strong></div><div><span>测试覆盖</span><strong>{{data.summary.test_coverage}}%</strong></div>
      </section>
      <section id="map" class="workspace">
        <div class="map-stage">
          <div class="stage-head"><div><h1>系统依赖蓝图</h1><p>拖动节点重排结构，滚轮缩放，选择模块查看证据。</p></div><button class="toggle" :aria-pressed="showCycles" @click="showCycles=!showCycles"><span></span>循环路径</button></div>
          <DependencyGraph :nodes="data.nodes" :edges="data.edges" :selected="selectedId" :show-cycles="showCycles" @select="select"/>
          <div class="legend"><span><i class="normal"></i>稳定模块</span><span><i class="risk"></i>风险模块</span><span><i class="cycle"></i>循环依赖</span></div>
        </div>
        <aside class="inspector" :class="{open:mobilePanel}" aria-label="模块检查台">
          <button class="close-inspector" @click="mobilePanel=false" aria-label="关闭检查台"><PhX :size="20"/></button>
          <template v-if="selected">
            <div class="inspector-title"><span>{{selected.domain}}</span><h2>{{selected.label}}</h2><p>{{selected.language}} · {{selected.loc.toLocaleString()}} LOC</p></div>
            <div class="risk-score"><span>综合风险</span><strong>{{selected.risk}}</strong><small>/ 100</small></div>
            <div class="measure-list">
              <div><span>圈复杂度</span><b>{{selected.complexity}}</b><progress :value="selected.complexity" max="100"></progress></div>
              <div><span>近30天变更</span><b>{{selected.churn}}</b><progress :value="selected.churn" max="80"></progress></div>
              <div><span>测试覆盖率</span><b>{{selected.coverage}}%</b><progress class="inverse" :value="selected.coverage" max="100"></progress></div>
              <div><span>连接度</span><b>{{selected.degree}}</b><progress :value="selected.degree" max="10"></progress></div>
            </div>
            <article v-if="selectedInsight" class="diagnosis"><PhPath :size="20"/><div><h3>{{selectedInsight.title}}</h3><p>{{selectedInsight.detail}}</p></div></article>
            <div class="connections"><h3>直接依赖 <span>{{related.length}}</span></h3><button v-for="edge in related" :key="edge.source+edge.target" @click="select(edge.source===selectedId?edge.target:edge.source)"><code>{{edge.source}}</code><span>→</span><code>{{edge.target}}</code><b>{{edge.coupling}}</b></button></div>
          </template>
        </aside>
      </section>
      <section id="risks" class="risk-section"><header><h2>架构风险队列</h2><p>按影响范围和修复紧迫度排序。</p></header><div class="risk-list"><button v-for="(item,index) in data.insights" :key="item.module" @click="select(item.module)"><span class="risk-index">{{String(index+1).padStart(2,'0')}}</span><span class="severity" :class="item.severity">{{item.severity}}</span><strong>{{item.title}}</strong><p>{{item.detail}}</p><code>{{item.module}}</code></button></div></section>
      <section id="files" class="files-section"><header><h2>热点文件</h2><p>复杂度、变更频率与测试缺口的交集。</p></header><div class="file-table" role="table"><div class="file-row file-head" role="row"><span>路径</span><span>复杂度</span><span>变更</span><span>覆盖</span><span>作者</span></div><button class="file-row" v-for="file in data.hotspots" :key="file.path" @click="select(file.module)"><span><PhBracketsCurly :size="16"/><code>{{file.path}}</code></span><b>{{file.complexity}}</b><b>{{file.churn}}</b><b>{{file.coverage}}%</b><b>{{file.authors}}</b></button></div></section>
    </template>
  </main>
</div>
</template>
