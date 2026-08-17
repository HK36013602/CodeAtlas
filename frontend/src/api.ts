import type { Analysis } from './types';
export async function getAnalysis():Promise<Analysis>{const response=await fetch('/api/v1/analysis');if(!response.ok)throw new Error('无法读取架构分析结果');return response.json()}
export async function startScan(){const response=await fetch('/api/v1/scans',{method:'POST'});if(!response.ok)throw new Error('扫描任务未能提交');return response.json()}
export async function getScanStatus(taskId:string){const response=await fetch(`/api/v1/scans/${encodeURIComponent(taskId)}`);if(!response.ok)throw new Error('无法读取扫描进度');return response.json() as Promise<{status:string;error?:string}>}
