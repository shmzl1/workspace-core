<template>
<div class="h-full flex flex-col bg-background">
      <div class="max-w-container-max mx-auto space-y-gutter">
        <!-- Overview Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-gutter">
          <div class="glass-card rounded-xl p-6 relative overflow-hidden">
            <div class="absolute -right-4 -top-4 w-24 h-24 bg-primary-container/10 rounded-full blur-xl"></div>
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">今日面试总数</p>
                <h2 class="font-display text-display text-on-surface mt-1">12</h2>
              </div>
              <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">event</span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="font-body-md text-body-md text-secondary flex items-center gap-1">
                <span class="material-symbols-outlined text-[16px]">trending_up</span> 20%
              </span>
              <span class="font-label-md text-label-md text-on-surface-variant">较昨日</span>
            </div>
          </div>
          
          <div class="glass-card rounded-xl p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">待评价面试</p>
                <h2 class="font-display text-display text-on-surface mt-1">4</h2>
              </div>
              <div class="w-10 h-10 rounded-lg bg-[#FFF7ED] flex items-center justify-center text-[#EA580C]">
                <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">rate_review</span>
              </div>
            </div>
            <div class="w-full bg-surface-container h-2 rounded-full mt-4 overflow-hidden">
              <div class="bg-[#EA580C] h-full rounded-full" :style="{ width: '33%' }"></div>
            </div>
          </div>
          
          <div class="glass-card rounded-xl p-6">
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider">平均面试时长</p>
                <h2 class="font-display text-display text-on-surface mt-1">45<span class="font-headline-md text-headline-md ml-1 text-on-surface-variant">min</span></h2>
              </div>
              <div class="w-10 h-10 rounded-lg bg-tertiary/10 flex items-center justify-center text-tertiary">
                <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">timer</span>
              </div>
            </div>
            <div class="flex items-center gap-2 mt-4">
              <span class="material-symbols-outlined text-secondary text-[16px]">check_circle</span>
              <span class="font-label-md text-label-md text-on-surface-variant">符合标准预期时长</span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-gutter min-h-[600px]">
          <!-- Left: Calendar -->
          <div class="lg:col-span-4 glass-card rounded-xl p-6 flex flex-col h-full">
            <div class="flex justify-between items-center mb-6">
              <h3 class="font-title-lg text-title-lg text-on-surface">2023年 10月</h3>
              <div class="flex bg-surface-container-low rounded-lg p-1">
                <button class="px-3 py-1 rounded bg-white shadow-sm font-label-md text-label-md text-on-surface">月视图</button>
                <button class="px-3 py-1 rounded font-label-md text-label-md text-on-surface-variant hover:text-on-surface">周视图</button>
              </div>
            </div>
            
            <div class="grid grid-cols-7 gap-2 mb-2">
              <div class="text-center font-label-md text-label-md text-on-surface-variant py-2">一</div>
              <div class="text-center font-label-md text-label-md text-on-surface-variant py-2">二</div>
              <div class="text-center font-label-md text-label-md text-on-surface-variant py-2">三</div>
              <div class="text-center font-label-md text-label-md text-on-surface-variant py-2">四</div>
              <div class="text-center font-label-md text-label-md text-on-surface-variant py-2">五</div>
              <div class="text-center font-label-md text-label-md text-outline py-2">六</div>
              <div class="text-center font-label-md text-label-md text-outline py-2">日</div>
            </div>
            
            <div class="flex-1 grid grid-cols-7 gap-2">
              <!-- Example Days -->
              <div class="text-center py-2 text-outline">25</div>
              <div class="text-center py-2 text-outline">26</div>
              <div class="text-center py-2 text-outline">27</div>
              <div class="text-center py-2 text-outline">28</div>
              <div class="text-center py-2 text-outline">29</div>
              <div class="text-center py-2 text-outline">30</div>
              <div class="text-center py-2">1</div>
              
              <div class="text-center py-2">2</div>
              <div class="text-center py-2 relative">
                3
                <span class="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full"></span>
              </div>
              <div class="text-center py-2">4</div>
              <div class="text-center py-2 relative">
                5
                <span class="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full"></span>
              </div>
              <div class="text-center py-2">6</div>
              <div class="text-center py-2 text-outline">7</div>
              <div class="text-center py-2 text-outline">8</div>
              
              <div class="text-center py-2 relative">
                9
                <span class="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full"></span>
              </div>
              <div class="text-center py-2 bg-primary text-on-primary rounded-full font-bold shadow-md shadow-primary/30 relative flex items-center justify-center">
                10
              </div>
              <div class="text-center py-2 relative">
                11
                <span class="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full"></span>
              </div>
              <div class="text-center py-2">12</div>
              <div class="text-center py-2 relative">
                13
                <span class="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-primary rounded-full"></span>
              </div>
              <div class="text-center py-2 text-outline">14</div>
              <div class="text-center py-2 text-outline">15</div>
              
              <!-- Filler for visual -->
              <div class="text-center py-2">16</div><div class="text-center py-2">17</div><div class="text-center py-2">18</div><div class="text-center py-2">19</div><div class="text-center py-2">20</div><div class="text-center py-2 text-outline">21</div><div class="text-center py-2 text-outline">22</div>
            </div>
            
            <div class="mt-4 pt-4 border-t border-outline-variant">
              <h4 class="font-label-md text-label-md text-on-surface-variant mb-2">智能排期建议</h4>
              <div class="bg-surface-bright border border-primary/20 rounded-lg p-3 flex gap-3 items-start">
                <span class="material-symbols-outlined text-primary text-[20px]">smart_toy</span>
                <div>
                  <p class="font-body-md text-body-md text-on-surface text-sm">下周三下午有3个连续空闲时间段，建议安排后端工程师集中面试。</p>
                  <button class="text-primary font-label-md text-label-md mt-1 hover:underline">一键安排</button>
                </div>
              </div>

              <div class="bg-surface-container-lowest border border-outline-variant rounded-lg p-3 flex gap-3 items-start mt-3">
                <span class="material-symbols-outlined text-[#EA580C] text-[20px]">rule</span>
                <div>
                  <p class="font-body-md text-body-md text-on-surface text-sm">冲突检测：2 名面试官在 14:00 后不可用，A-301 会议室 16:00 前空闲。</p>
                  <button class="text-primary font-label-md text-label-md mt-1 hover:underline">查看推荐时段</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: Interview List -->
          <div class="lg:col-span-8 glass-card rounded-xl p-0 flex flex-col h-full overflow-hidden">
            <div class="p-6 border-b border-outline-variant flex justify-between items-center bg-surface/50">
              <h3 class="font-title-lg text-title-lg text-on-surface">10月10日 面试日程</h3>
              <div class="flex gap-2">
                <button class="px-3 py-1.5 bg-primary text-on-primary rounded-lg font-label-md text-label-md flex items-center gap-1 hover:bg-primary/90 transition-colors">
                  <span class="material-symbols-outlined text-[16px]">auto_awesome</span> 智能排期
                </button>
                <button class="px-3 py-1.5 border border-outline-variant rounded-lg font-label-md text-label-md text-on-surface flex items-center gap-1 hover:bg-surface-container-low transition-colors">
                  <span class="material-symbols-outlined text-[16px]">filter_list</span> 筛选
                </button>
              </div>
            </div>
            
            <div class="flex-1 overflow-y-auto p-6 space-y-4">
              <!-- Interview Item 1 (Active/Now) -->
              <div class="border-2 border-primary rounded-xl p-4 flex items-center gap-6 bg-primary/5 relative shadow-sm">
                <div class="absolute left-0 top-0 bottom-0 w-1.5 bg-primary rounded-l-lg"></div>
                <div class="flex flex-col items-center justify-center min-w-[80px]">
                  <span class="font-headline-md text-headline-md text-primary font-bold">10:00</span>
                  <span class="font-label-md text-label-md text-on-surface-variant">11:00</span>
                  <span class="mt-1 px-2 py-0.5 bg-error/10 text-error font-label-md text-[10px] rounded animate-pulse">进行中</span>
                </div>
                <div class="w-12 h-12 rounded-full bg-surface-container-high overflow-hidden shrink-0">
                  <img class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCujGbtJhx-5bGV6XBd8lxwcoj73-LbJcIWSZgHTEhkGIRl7d9n4MGFQZRwS-Egp2OzKRIto_l4e-tP91flIVU3doTKFdFqB0Ajt9Ai6W61Gr50of-n9Dor17lDqqg3haYuXVn3unq-1tCbGFYYlhoiG86fpr3Sr3XNcCohzorrCVO7PdaJeWdN6KDFj_2u7Io150uNqGTqgrRoIsmfC8lhEWBd-Z1LJG5ywMyagizqZmSrXnznSwcZi9-9TkBRHxQiJ_ox3zcB7Bs_" />
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <h4 class="font-title-lg text-title-lg text-on-surface">张伟</h4>
                    <span class="px-2 py-0.5 bg-surface-container text-on-surface-variant rounded text-xs font-label-md">资深前端工程师</span>
                  </div>
                  <div class="flex items-center gap-4 font-body-md text-body-md text-on-surface-variant text-sm">
                    <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">person</span> 面试官: 李强 (技术总监)</span>
                    <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">videocam</span> 线上 - 腾讯会议</span>
                  </div>
                </div>
                <div class="flex flex-col gap-2 shrink-0">
                  <button class="px-4 py-2 bg-primary text-on-primary rounded-lg font-label-md text-label-md hover:bg-primary-fixed-dim hover:text-on-primary-fixed transition-colors flex items-center justify-center gap-1">
                    <span class="material-symbols-outlined text-[18px]">meeting_room</span> 进入房间
                  </button>
                  <button class="px-4 py-2 bg-white border border-outline-variant text-on-surface rounded-lg font-label-md text-label-md hover:bg-surface-container-low transition-colors">
                    查看简历
                  </button>
                </div>
              </div>
              
              <!-- Interview Item 2 (Upcoming) -->
              <div class="border border-outline-variant rounded-xl p-4 flex items-center gap-6 bg-white hover:border-primary/50 transition-colors group">
                <div class="flex flex-col items-center justify-center min-w-[80px]">
                  <span class="font-title-lg text-title-lg text-on-surface">14:00</span>
                  <span class="font-label-md text-label-md text-on-surface-variant">14:45</span>
                </div>
                <div class="w-12 h-12 rounded-full bg-surface-container-high overflow-hidden shrink-0">
                  <img class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBFV9wa9Aa2eJ5lKlbaY2jm9gCqySZckOGrnQ2oqXLgP7VrBYlqxqKmJj5BpNhwC-fiKBtuU_vnOH9Y6trJLXqmcbk1MMtMm-g4it1UmSr7R4ot-8bARZ9BtykW619ZLDPNKR4HVZHnP845sq5utQ4fMZWHXWpG1Vw-gXd8NZDbtIAJVNUkcQsBVpX5YnTGdVRYbxlw2AT7RSzgXNKDJHdO8DmJRnnCkk6ceU0CCVsNpgyeOQMpMOccPWU2lRfgdTMwI_wJcZVAFbaW" />
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <h4 class="font-title-lg text-title-lg text-on-surface group-hover:text-primary transition-colors">王芳</h4>
                    <span class="px-2 py-0.5 bg-surface-container text-on-surface-variant rounded text-xs font-label-md">产品经理</span>
                  </div>
                  <div class="flex items-center gap-4 font-body-md text-body-md text-on-surface-variant text-sm">
                    <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">person</span> 面试官: 赵敏 (产品VP)</span>
                    <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">location_on</span> 线下 - 创新会议室A</span>
                  </div>
                </div>
                <div class="flex flex-col gap-2 shrink-0">
                  <button class="px-4 py-2 bg-white border border-outline-variant text-on-surface rounded-lg font-label-md text-label-md hover:bg-surface-container-low transition-colors">
                    查看简历
                  </button>
                </div>
              </div>
              
              <!-- Interview Item 3 (Upcoming) -->
              <div class="border border-outline-variant rounded-xl p-4 flex items-center gap-6 bg-white hover:border-primary/50 transition-colors group">
                <div class="flex flex-col items-center justify-center min-w-[80px]">
                  <span class="font-title-lg text-title-lg text-on-surface">16:30</span>
                  <span class="font-label-md text-label-md text-on-surface-variant">17:30</span>
                </div>
                <div class="w-12 h-12 rounded-full bg-surface-container-high flex items-center justify-center shrink-0 text-on-surface-variant font-bold text-lg">
                  L
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <h4 class="font-title-lg text-title-lg text-on-surface group-hover:text-primary transition-colors">刘伟</h4>
                    <span class="px-2 py-0.5 bg-surface-container text-on-surface-variant rounded text-xs font-label-md">UI/UX设计师</span>
                  </div>
                  <div class="flex items-center gap-4 font-body-md text-body-md text-on-surface-variant text-sm">
                    <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">person</span> 面试官: 智能初筛</span>
                    <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">videocam</span> 线上 - AI 面试间</span>
                  </div>
                </div>
                <div class="flex flex-col gap-2 shrink-0">
                  <button class="px-4 py-2 bg-white border border-outline-variant text-on-surface rounded-lg font-label-md text-label-md hover:bg-surface-container-low transition-colors">
                    查看配置
                  </button>
                </div>
              </div>
              
              <!-- Finished Interview -->
              <div class="border border-outline-variant rounded-xl p-4 flex items-center gap-6 bg-surface-container-low opacity-75">
                <div class="flex flex-col items-center justify-center min-w-[80px]">
                  <span class="font-title-lg text-title-lg text-outline">09:00</span>
                  <span class="font-label-md text-label-md text-outline">09:45</span>
                </div>
                <div class="w-12 h-12 rounded-full bg-surface-container-high overflow-hidden shrink-0 grayscale">
                  <img class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCQM20XGKART589Zm5UqZbi28EBVzNS2N0aV-KUO-vB3RG9RWXMkP3u3jse1eqO0G6-dKoxK_VBq01FoiAu84qM52xfYxk19a0UbtThoxi0A5BZXG9S7FLmF7CEMwwksOV92WOt9MuO7RIXI90QpKUxsAEGxTuaRpW9V3NMq-hLzSp28x4WG_0FsXzhi5preqlLkuAJyg1DXA86DHAW90Sypgj5IrvxemH8S8WtJCLMNkjf1PL1RTV9dBeOrOC-UtLPWzflZF3_Th2Z" />
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <h4 class="font-title-lg text-title-lg text-outline">陈晓</h4>
                    <span class="px-2 py-0.5 bg-surface-container text-outline rounded text-xs font-label-md">数据分析师</span>
                    <span class="px-2 py-0.5 bg-secondary/10 text-secondary rounded text-xs font-label-md ml-auto">已结束</span>
                  </div>
                  <div class="flex items-center gap-4 font-body-md text-body-md text-outline text-sm">
                    <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">person</span> 面试官: 王刚 (数据面试官)</span>
                  </div>
                </div>
                <div class="flex flex-col gap-2 shrink-0">
                  <button class="px-4 py-2 bg-[#FFF7ED] text-[#EA580C] border border-[#EA580C]/20 rounded-lg font-label-md text-label-md hover:bg-[#FFEDD5] transition-colors">
                    填写评价
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- FAB -->
      <button class="fixed bottom-28 right-8 w-14 h-14 bg-primary text-on-primary rounded-full shadow-lg flex items-center justify-center hover:bg-primary-fixed-dim hover:text-on-primary-fixed hover:scale-105 transition-all duration-200 z-50">
        <span class="material-symbols-outlined text-3xl">add</span>
      </button>
    </div>
</template>

<script setup lang="ts">
</script>
