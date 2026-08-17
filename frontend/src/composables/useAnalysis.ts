import { computed, ref } from 'vue'
import { getAnalysis, getScanStatus, startScan } from '../api'
import type { Analysis } from '../types'

const data=ref<Analysis>();const loading=ref(false);const error=ref('');const selectedId=ref('');const scanning=ref(false)
const selected=computed(()=>data.value?.nodes.find(n=>n.id===selectedId.value))
const related=computed(()=>data.value?.edges.filter(e=>e.source===selectedId.value||e.target===selectedId.value)||[])
const selectedInsight=computed(()=>data.value?.insights.find(i=>i.module===selectedId.value))
const pause=(ms:number)=>new Promise(resolve=>setTimeout(resolve,ms))
async function load(analysisId?:number){loading.value=true;error.value='';try{data.value=await getAnalysis(analysisId);if(!data.value.nodes.some(n=>n.id===selectedId.value))selectedId.value=data.value.nodes[0]?.id||''}catch(e){error.value=e instanceof Error?e.message:'加载失败'}finally{loading.value=false}}
async function ensureLoaded(){if(!data.value&&!loading.value)await load()}
async function scan(){scanning.value=true;error.value='';try{const queued=await startScan();for(let attempt=0;attempt<30;attempt+=1){await pause(400);const task=await getScanStatus(queued.task_id);if(task.status==='success'){await load();return}if(task.status==='failure')throw new Error(task.error||'扫描失败')}throw new Error('扫描仍在进行，请稍后刷新。')}catch(e){error.value=e instanceof Error?e.message:'扫描失败'}finally{scanning.value=false}}
const fmt=(n:number)=>n>=1000?`${(n/1000).toFixed(1)}k`:String(n)
export function useAnalysis(){return{data,loading,error,selectedId,scanning,selected,related,selectedInsight,load,ensureLoaded,scan,fmt}}
