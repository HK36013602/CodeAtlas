export interface ModuleNode {id:string;label:string;language:string;domain:string;loc:number;complexity:number;churn:number;coverage:number;risk:number;degree:number}
export interface Edge {source:string;target:string;calls:number;coupling:number;cyclic:boolean}
export interface Hotspot {path:string;module:string;language:string;complexity:number;churn:number;coverage:number;authors:number;last_changed:string}
export interface Insight {severity:string;title:string;detail:string;module:string}
export interface Analysis {repository:{name:string;branch:string;commit:string;languages:Record<string,number>;synthetic:boolean;scanned_at:string};summary:Record<string,number>;nodes:ModuleNode[];edges:Edge[];cycles:string[][];hotspots:Hotspot[];insights:Insight[]}
