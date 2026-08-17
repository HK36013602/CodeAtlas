<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import * as echarts from 'echarts/core';
import { GraphChart } from 'echarts/charts';
import { TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import type { Edge, ModuleNode } from '../types';
echarts.use([GraphChart, TooltipComponent, CanvasRenderer]);
const props=defineProps<{nodes:ModuleNode[];edges:Edge[];selected:string;showCycles:boolean}>();
const emit=defineEmits<{select:[id:string]}>();
const root=ref<HTMLDivElement>(); let chart:echarts.ECharts|undefined;
const categories=computed(()=>[...new Set(props.nodes.map(n=>n.domain))].map(name=>({name})));
function render(){if(!chart||!props.nodes.length)return;const domains=categories.value.map(c=>c.name);chart.setOption({animationDurationUpdate:240,tooltip:{backgroundColor:'#17201e',borderWidth:0,textStyle:{color:'#f4f6f5',fontFamily:'Manrope'},formatter:(p:any)=>p.dataType==='node'?`<b>${p.data.label}</b><br/>${p.data.language} · 风险 ${p.data.risk}<br/>${p.data.loc.toLocaleString()} LOC`:`${p.data.source} → ${p.data.target}<br/>调用 ${p.data.calls} 次`},series:[{type:'graph',layout:'force',roam:true,draggable:true,force:{repulsion:360,edgeLength:[95,210],gravity:.08},categories:categories.value,data:props.nodes.map(n=>({...n,category:domains.indexOf(n.domain),symbolSize:24+n.degree*5,itemStyle:{color:n.id===props.selected?'#f0a33a':n.risk>=65?'#42504c':'#dce3e1',borderColor:n.risk>=65?'#f0a33a':'#52605c',borderWidth:n.id===props.selected?4:1.5},label:{show:true,position:'right',color:'#27322f',fontFamily:'JetBrains Mono',fontSize:11}})),links:props.edges.map(e=>({...e,lineStyle:{color:e.cyclic&&props.showCycles?'#d27b22':'#8b9995',width:e.cyclic&&props.showCycles?2.4:Math.max(1,e.coupling/40),opacity:e.cyclic&&props.showCycles?.95:.34,curveness:e.cyclic?.16:.04}})),emphasis:{focus:'adjacency',lineStyle:{opacity:1,width:3}},edgeSymbol:['none','arrow'],edgeSymbolSize:6}]},true)}
onMounted(()=>{chart=echarts.init(root.value!);chart.on('click',(p:any)=>{if(p.dataType==='node')emit('select',p.data.id)});render();window.addEventListener('resize',resize)});function resize(){chart?.resize()}watch(()=>[props.nodes,props.selected,props.showCycles],render,{deep:true});onBeforeUnmount(()=>{window.removeEventListener('resize',resize);chart?.dispose()});
</script>
<template><div ref="root" class="dependency-graph" role="img" aria-label="模块依赖关系图"></div></template>
