<template>
<div class="flex-1 flex flex-col h-[calc(100vh-64px)] relative overflow-hidden bg-surface">
      <!-- Background Decorative -->
      <div class="absolute top-[20%] -left-[10%] w-96 h-96 bg-primary/10 rounded-full blur-[100px] pointer-events-none" />
      <div class="absolute bottom-[-10%] right-[10%] w-80 h-80 bg-secondary-container/20 rounded-full blur-[80px] pointer-events-none" />

      <div class="flex-1 overflow-y-auto p-4 md:p-8 flex flex-col xl:flex-row gap-8 max-w-[1600px] mx-auto w-full z-10">
        
        <!-- Main Chat Area -->
        <div class="flex-1 bg-surface-container-lowest/80 rounded-2xl border border-outline-variant/40 shadow-xl shadow-primary/5 flex flex-col overflow-hidden glass-card">
          
          <!-- Chat Header -->
          <div class="px-6 py-4 border-b border-outline-variant/40 bg-surface-container-lowest/50 backdrop-blur-md flex justify-between items-center relative overflow-hidden">
            <div class="flex items-center gap-4 relative z-10">
              <div class="relative w-12 h-12">
                <div class="absolute inset-0 bg-gradient-to-tr from-primary to-tertiary rounded-xl blur-[8px] opacity-60 animate-pulse" />
                <div class="relative w-12 h-12 rounded-xl bg-surface-container-lowest border border-primary/20 flex items-center justify-center text-primary shadow-sm z-10">
                  <span class="material-symbols-outlined text-[28px] bg-clip-text text-transparent bg-gradient-to-r from-primary to-tertiary">smart_toy</span>
                </div>
              </div>
              <div>
                <h2 class="text-lg font-bold text-on-surface m-0 bg-clip-text text-transparent bg-gradient-to-r from-on-surface to-on-surface-variant">TalentOS 智能助手</h2>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                  </span>
                  <p class="text-xs font-medium text-emerald-600 m-0">上下文引擎已激活</p>
                </div>
              </div>
            </div>
            <div class="flex gap-2">
              <button class="w-9 h-9 rounded-lg border border-outline-variant/50 flex items-center justify-center text-on-surface-variant hover:bg-surface-container-low transition-colors">
                <span class="material-symbols-outlined text-[20px]">restart_alt</span>
              </button>
            </div>
          </div>

          <!-- Chat History -->
          <div class="flex-1 overflow-y-auto p-6 flex flex-col gap-6 no-scrollbar">
            
            <div class="flex justify-center sticky top-0 z-20">
              <span class="bg-surface-container-lowest/90 backdrop-blur-sm border border-outline-variant/40 text-on-surface-variant text-[11px] font-medium px-4 py-1.5 rounded-full shadow-sm">
                今天, 10:42 AM
              </span>
            </div>

            <!-- User Message -->
            <div class="flex justify-end group">
              <div class="bg-on-surface text-surface-container-lowest rounded-2xl rounded-tr-sm px-5 py-3.5 max-w-[80%] shadow-md">
                <p class="text-sm m-0">你能总结一下今年的公司休假政策吗？特别是关于假期结转的规定。</p>
              </div>
              <div class="w-8 h-8 rounded-full overflow-hidden border border-outline-variant ml-3 shadow-sm self-end shrink-0">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCrxqatEHDCXw88vrI_yjVcbb-S0UQKZYDPRmMJ2L8wJtEy0DYS0i0W4nE1L0U_Ks54MgkryE9ck-_dfxqWl3lHFBEY5lCh1xmnR1TuPSnQvchrafaVeAP8WibX2NHz92gFp_qqqTLrrVRtn_T0BSqFVOrSXUoOgk4-Be9JXUpzeU7aqHTP8-LZ7eeY_yQYWohSQOKQbzxch1Q-aF_ZrcDOImPm6QzaN1mjOAari_cfazlK_Bwy4H01sjsVz9SvVoTqomLOvf5bJdVO" alt="User" class="w-full h-full object-cover" />
              </div>
            </div>

            <!-- Intelligent process block -->
            <div class="flex justify-start pl-11 mb-2">
              <div class="bg-surface-container-low/50 rounded-xl p-4 border border-outline-variant/30 text-sm max-w-[85%] w-full shadow-inner">
                <div class="flex items-center gap-2 mb-3 text-primary text-xs font-bold uppercase tracking-wide">
                  <span class="material-symbols-outlined text-[16px] animate-spin" :style="{ animationDuration: '3s' }">memory</span> 
                  推理链路
                </div>
                
                <div class="relative h-20 w-full bg-surface-container-lowest/50 rounded-lg border border-outline-variant/30 overflow-hidden mb-3 p-3 flex justify-between items-center px-8">
                  <!-- Nodes -->
                  <div class="flex flex-col items-center gap-1 z-10">
                    <div class="w-8 h-8 rounded-full bg-surface border-2 border-primary/40 flex items-center justify-center text-primary/70">
                      <span class="material-symbols-outlined text-[16px]">parse</span>
                    </div>
                    <span class="text-[10px] text-outline font-medium">解析意图</span>
                  </div>
                  
                  <div class="flex-1 h-0.5 bg-primary/30 mx-2" />
                  
                  <div class="flex flex-col items-center gap-1 z-10">
                    <div class="w-8 h-8 rounded-full bg-surface border-2 border-primary flex items-center justify-center text-primary shadow-[0_0_10px_rgba(27,77,255,0.3)] scale-110">
                      <span class="material-symbols-outlined text-[16px]">database</span>
                    </div>
                    <span class="text-[10px] text-primary font-bold">向量搜索</span>
                  </div>
                  
                  <div class="flex-1 h-0.5 bg-outline-variant/50 mx-2" />
                  
                  <div class="flex flex-col items-center gap-1 z-10">
                    <div class="w-8 h-8 rounded-full bg-surface border-2 border-outline-variant flex items-center justify-center text-on-surface-variant">
                      <span class="material-symbols-outlined text-[16px]">check_circle</span>
                    </div>
                    <span class="text-[10px] text-outline font-medium">综合分析</span>
                  </div>
                </div>

                <div class="space-y-1.5 font-mono text-[11px] text-on-surface-variant">
                  <div class="flex items-center gap-2 opacity-60">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span>已解析意图："假期政策摘要" + "结转规则"</span>
                  </div>
                  <div class="flex items-center gap-2 text-primary font-medium">
                    <span class="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                    <span>正在查询政策数据库 (相似度评分: 0.94)...</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Assistant message -->
            <div class="flex justify-start gap-3 relative z-10">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/20 to-tertiary/20 border border-primary/30 flex items-center justify-center text-primary shrink-0 mt-1 shadow-sm backdrop-blur-sm">
                <span class="material-symbols-outlined text-[20px]">auto_awesome</span>
              </div>
              
              <div class="bg-surface-container-lowest border border-primary/30 rounded-2xl rounded-tl-sm p-6 max-w-[85%] ai-glow glass-card relative overflow-hidden group">
                <p class="text-sm text-on-surface m-0 mb-4 leading-relaxed relative z-10">
                  根据从政策中心检索到的最新 <strong>员工手册 (v2024.1)</strong>，以下是关于假期结转政策的摘要：
                </p>
                <ul class="list-disc pl-5 text-sm text-on-surface space-y-2 mb-5 relative z-10">
                  <li>员工最多可将 <strong>5 天未使用的年假</strong> 结转至下一日历年。</li>
                  <li>这些结转的假期必须在次年的 <strong>3月31日</strong> 之前使用。</li>
                  <li>任何在 3月31日 之前未使用的结转假期将被作废。</li>
                </ul>

                <!-- Source Citation -->
                <div class="bg-surface-container-low/70 rounded-xl p-4 border border-outline-variant/40 mt-2 relative overflow-hidden group-hover:border-primary/40 transition-colors">
                  <div class="absolute top-0 left-0 w-1 h-full bg-primary rounded-l-xl" />
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex items-center gap-2">
                      <div class="p-1.5 bg-primary/10 rounded-lg text-primary">
                        <span class="material-symbols-outlined text-[18px]">menu_book</span>
                      </div>
                      <h4 class="text-sm font-semibold text-on-surface m-0">员工手册 2024</h4>
                    </div>
                    <div class="flex items-center gap-1.5 px-2 py-1 bg-emerald-100 border border-emerald-200 rounded-full text-emerald-700 font-medium text-[10px]">
                      <span class="material-symbols-outlined text-[12px]">verified</span> 高置信度
                    </div>
                  </div>
                  
                  <button class="w-full flex items-center justify-between px-3 py-2 bg-surface-container-lowest hover:bg-primary/5 border border-outline-variant/40 hover:border-primary/40 rounded-lg transition-colors text-primary text-[13px] font-medium">
                    <span>查看完整政策文档</span>
                    <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Input Area -->
          <div class="p-5 border-t border-outline-variant/40 bg-surface-container-lowest/80 backdrop-blur-xl z-20">
            <!-- Suggestions -->
            <div class="flex gap-2 overflow-x-auto no-scrollbar pb-3 mb-2">
              <button class="whitespace-nowrap px-4 py-2 rounded-xl border border-outline-variant/60 bg-surface-container-lowest/50 text-on-surface text-sm hover:border-primary/50 hover:bg-primary/5 hover:text-primary transition-all flex items-center gap-2 shadow-sm font-medium">
                <span class="material-symbols-outlined text-[18px] text-primary/70">beach_access</span> 剩余假期查询
              </button>
              <button class="whitespace-nowrap px-4 py-2 rounded-xl border border-outline-variant/60 bg-surface-container-lowest/50 text-on-surface text-sm hover:border-primary/50 hover:bg-primary/5 hover:text-primary transition-all flex items-center gap-2 shadow-sm font-medium">
                <span class="material-symbols-outlined text-[18px] text-emerald-600/70">payments</span> 查看最新工资单
              </button>
            </div>
            
            <div class="relative group">
              <div class="absolute -inset-0.5 bg-gradient-to-r from-primary/30 to-tertiary/30 rounded-2xl blur opacity-30 group-hover:opacity-60 transition duration-500" />
              <div class="relative flex items-center bg-surface-container-lowest border border-outline-variant/50 rounded-2xl shadow-inner overflow-hidden focus-within:ring-1 focus-within:ring-primary focus-within:border-primary transition-all">
                <div class="pl-4 pr-2 flex items-center text-primary">
                  <span class="material-symbols-outlined text-[24px]">auto_awesome</span>
                </div>
                <input 
                  type="text" 
                  placeholder="问问智能助手任何事..." 
                  class="w-full h-14 bg-transparent border-none focus:ring-0 text-sm text-on-surface placeholder:text-outline/60 px-2 outline-none"
                />
                <div class="pr-2 flex gap-1">
                  <button class="w-10 h-10 rounded-xl flex items-center justify-center text-outline hover:text-on-surface hover:bg-surface-container-low transition-colors">
                    <span class="material-symbols-outlined text-[20px]">mic</span>
                  </button>
                  <button class="w-12 h-10 rounded-xl bg-gradient-to-r from-primary to-primary-container text-white flex items-center justify-center hover:shadow-lg hover:shadow-primary/30 transition-all ml-1">
                    <span class="material-symbols-outlined text-[20px]">send</span>
                  </button>
                </div>
              </div>
            </div>
            <div class="text-center mt-3">
              <span class="text-[10px] text-outline/70 font-medium">智能建议可能存在偏差，请核实重要信息。</span>
            </div>
          </div>
        </div>

        <!-- Right Sidebar Dashboard (Desktop) -->
        <div class="hidden xl:flex w-[340px] flex-col gap-5 z-10">
          <div class="bg-gradient-to-br from-primary/5 to-tertiary/5 rounded-2xl border border-primary/20 shadow-lg p-5 relative overflow-hidden glass-card">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                <span class="material-symbols-outlined text-[18px]">insights</span>
              </div>
              <h3 class="text-base font-semibold text-on-surface m-0">智能洞察</h3>
            </div>
            <p class="text-[13px] text-on-surface-variant m-0 leading-relaxed">
              根据您最近的查询，您可能正在计划休假。您还有 <strong class="text-primary font-semibold">14.5 天</strong> 余额。如果您在即将到来的假期中使用 5 天，明年您仍可结转 <strong class="text-primary font-semibold">4.5 天</strong>。
            </p>
            <button class="mt-4 w-full py-2 px-4 bg-surface-container-lowest border border-primary/30 rounded-lg text-primary text-xs font-semibold hover:bg-primary/5 transition-colors flex items-center justify-center gap-2">
              <span class="material-symbols-outlined text-[16px]">edit_calendar</span> 起草休假申请
            </button>
          </div>

          <div class="bg-surface-container-lowest/80 rounded-2xl border border-outline-variant/40 shadow-lg p-5 glass-card">
            <h3 class="text-base font-semibold text-on-surface m-0 mb-5 flex items-center gap-2">
              <span class="material-symbols-outlined text-outline text-[20px]">dashboard</span> 我的仪表板
            </h3>
            
            <div class="space-y-5">
              <div>
                <div class="flex justify-between items-end mb-2">
                  <div>
                    <span class="text-[10px] text-outline uppercase tracking-wider font-bold block mb-1">剩余年假</span>
                    <div class="flex items-baseline gap-1">
                      <span class="text-3xl font-bold text-on-surface leading-none">14.5</span>
                      <span class="text-xs text-on-surface-variant font-medium">/ 20 天</span>
                    </div>
                  </div>
                  <div class="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center text-primary-container">
                    <span class="material-symbols-outlined text-[20px]">flight_takeoff</span>
                  </div>
                </div>
                <div class="w-full bg-surface-variant h-2 rounded-full mt-3 overflow-hidden">
                  <div class="bg-gradient-to-r from-primary to-tertiary h-full rounded-full" :style="{ width: '72%' }" />
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
</template>

<script setup lang="ts">
</script>
