<template>
<div class="flex-1 h-full">
      <div class="max-w-container-max mx-auto grid grid-cols-1 lg:grid-cols-12 gap-gutter">
        <!-- Left Column: Data & Reports -->
        <div class="lg:col-span-8 flex flex-col gap-gutter">
          
          <!-- Header -->
          <div class="flex justify-between items-end">
            <div>
              <h2 class="font-headline-lg text-headline-lg text-on-surface mb-1">薪资明细</h2>
              <p class="font-body-md text-body-md text-on-surface-variant">2023年 10月 | 研发中心 - 高级工程师</p>
            </div>
            <button class="bg-surface-container-lowest border border-outline-variant text-primary font-label-md text-label-md py-2 px-4 rounded-lg flex items-center gap-2 hover:bg-surface-container-low transition-colors shadow-sm">
              <span class="material-symbols-outlined text-[18px]">download</span>
              导出 PDF
            </button>
          </div>

          <!-- Hero Card: Net Pay -->
          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 p-6 shadow-sm relative overflow-hidden">
            <div class="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4"></div>
            <div class="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
              <div>
                <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-wider mb-2">本月实发工资 (CNY)</p>
                <div class="font-display text-[48px] leading-[56px] font-bold text-on-surface tracking-tight mb-2">
                  ¥ 28,450.00
                </div>
                <div class="flex items-center gap-2 text-secondary">
                  <span class="material-symbols-outlined text-[16px]">trending_up</span>
                  <span class="font-label-md text-label-md">较上月增长 2.4%</span>
                </div>
              </div>
              <div class="w-full md:w-auto flex gap-4">
                <div class="bg-surface-container-low p-4 rounded-lg flex-1 md:w-32 border border-outline-variant/30">
                  <p class="font-label-md text-label-md text-on-surface-variant mb-1">应发总额</p>
                  <p class="font-title-lg text-title-lg text-on-surface">35,000</p>
                </div>
                <div class="bg-surface-container-low p-4 rounded-lg flex-1 md:w-32 border border-outline-variant/30">
                  <p class="font-label-md text-label-md text-on-surface-variant mb-1">代扣代缴</p>
                  <p class="font-title-lg text-title-lg text-on-surface">6,550</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Breakdown Table -->
          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 shadow-sm overflow-hidden">
            <div class="px-6 py-4 border-b border-outline-variant/30 bg-surface-container-low/50 flex justify-between items-center">
              <h3 class="font-title-lg text-title-lg text-on-surface">薪资构成明细</h3>
              <button class="text-primary hover:bg-primary-container/10 p-1 rounded transition-colors">
                <span class="material-symbols-outlined">info</span>
              </button>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="bg-surface-container-low/50 border-b border-outline-variant/30">
                    <th class="py-3 px-6 font-label-md text-label-md uppercase text-on-surface-variant/70 font-medium w-1/3">项目</th>
                    <th class="py-3 px-6 font-label-md text-label-md uppercase text-on-surface-variant/70 font-medium">金额 (¥)</th>
                    <th class="py-3 px-6 font-label-md text-label-md uppercase text-on-surface-variant/70 font-medium text-right">说明</th>
                  </tr>
                </thead>
                <tbody class="font-body-md text-body-md text-on-surface divide-y divide-outline-variant/20">
                  <!-- Income Items -->
                  <tr class="hover:bg-surface-container-lowest transition-colors group">
                    <td class="py-3 px-6 flex items-center gap-2">
                      <div class="w-2 h-2 rounded-full bg-secondary"></div>
                      基本工资
                    </td>
                    <td class="py-3 px-6 font-medium">25,000.00</td>
                    <td class="py-3 px-6 text-right text-on-surface-variant text-sm">--</td>
                  </tr>
                  <tr class="hover:bg-surface-container-lowest transition-colors group">
                    <td class="py-3 px-6 flex items-center gap-2">
                      <div class="w-2 h-2 rounded-full bg-secondary"></div>
                      绩效奖金
                    </td>
                    <td class="py-3 px-6 font-medium">8,000.00</td>
                    <td class="py-3 px-6 text-right text-on-surface-variant text-sm">A 级绩效</td>
                  </tr>
                  <tr class="hover:bg-surface-container-lowest transition-colors group">
                    <td class="py-3 px-6 flex items-center gap-2">
                      <div class="w-2 h-2 rounded-full bg-secondary"></div>
                      各类津贴
                    </td>
                    <td class="py-3 px-6 font-medium">2,000.00</td>
                    <td class="py-3 px-6 text-right text-on-surface-variant text-sm">交通餐饮补贴</td>
                  </tr>
                  <!-- Deduction Items -->
                  <tr class="hover:bg-surface-container-lowest transition-colors group bg-error-container/5">
                    <td class="py-3 px-6 flex items-center gap-2 text-on-surface-variant">
                      <div class="w-2 h-2 rounded-full bg-error"></div>
                      社保公积金 (个人)
                    </td>
                    <td class="py-3 px-6 font-medium text-on-surface-variant">-4,200.00</td>
                    <td class="py-3 px-6 text-right text-on-surface-variant text-sm">基数: 25000</td>
                  </tr>
                  <tr class="hover:bg-surface-container-lowest transition-colors group bg-error-container/5">
                    <td class="py-3 px-6 flex items-center gap-2 text-on-surface-variant">
                      <div class="w-2 h-2 rounded-full bg-error"></div>
                      个人所得税
                    </td>
                    <td class="py-3 px-6 font-medium text-on-surface-variant">-2,350.00</td>
                    <td class="py-3 px-6 text-right text-on-surface-variant text-sm">已扣除专项附加</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="bg-surface-container-low font-title-lg text-title-lg">
                    <td class="py-4 px-6">实发合计</td>
                    <td class="py-4 px-6 text-primary" colspan="2">28,450.00</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- Annual Trend Chart Area -->
          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 shadow-sm p-6 mb-8">
            <div class="flex justify-between items-center mb-6">
              <h3 class="font-title-lg text-title-lg text-on-surface">年度收入趋势</h3>
              <select class="bg-surface-container-low border-none text-body-md rounded-md py-1 px-3 focus:ring-primary cursor-pointer outline-none">
                <option>2023</option>
                <option>2022</option>
              </select>
            </div>
            
            <!-- Placeholder for Chart -->
            <div class="h-64 w-full bg-surface-container-low/30 rounded-lg relative overflow-hidden flex items-end justify-between px-4 pb-0 pt-8 gap-2">
              <div class="w-full bg-primary/20 hover:bg-primary/40 transition-colors rounded-t-sm relative group cursor-pointer" :style="{ height: '60%' }">
                <div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-inverse-surface text-inverse-on-surface text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity">1月</div>
              </div>
              <div class="w-full bg-primary/20 hover:bg-primary/40 transition-colors rounded-t-sm relative group cursor-pointer" :style="{ height: '65%' }"></div>
              <div class="w-full bg-primary/20 hover:bg-primary/40 transition-colors rounded-t-sm relative group cursor-pointer" :style="{ height: '62%' }"></div>
              <div class="w-full bg-primary/20 hover:bg-primary/40 transition-colors rounded-t-sm relative group cursor-pointer" :style="{ height: '68%' }"></div>
              <div class="w-full bg-primary/20 hover:bg-primary/40 transition-colors rounded-t-sm relative group cursor-pointer" :style="{ height: '65%' }"></div>
              <div class="w-full bg-primary/20 hover:bg-primary/40 transition-colors rounded-t-sm relative group cursor-pointer" :style="{ height: '70%' }"></div>
              <div class="w-full bg-primary/20 hover:bg-primary/40 transition-colors rounded-t-sm relative group cursor-pointer" :style="{ height: '75%' }"></div>
              <div class="w-full bg-primary/20 hover:bg-primary/40 transition-colors rounded-t-sm relative group cursor-pointer" :style="{ height: '72%' }"></div>
              <div class="w-full bg-primary/20 hover:bg-primary/40 transition-colors rounded-t-sm relative group cursor-pointer" :style="{ height: '78%' }"></div>
              <div class="w-full bg-primary transition-colors rounded-t-sm relative group cursor-pointer shadow-[0_0_15px_rgba(27,77,255,0.3)]" :style="{ height: '85%' }">
                <div class="absolute -top-8 left-1/2 -translate-x-1/2 bg-inverse-surface text-inverse-on-surface text-xs py-1 px-2 rounded">10月</div>
              </div>
              <div class="w-full bg-surface-dim rounded-t-sm" :style="{ height: '10%' }"></div>
              <div class="w-full bg-surface-dim rounded-t-sm" :style="{ height: '10%' }"></div>
            </div>
            <div class="flex justify-between mt-2 text-xs text-outline font-label-md px-2">
              <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span><span>Jul</span><span>Aug</span><span>Sep</span><span class="text-primary font-bold">Oct</span><span>Nov</span><span>Dec</span>
            </div>
          </div>
        </div>

        <!-- Right Column: AI Assistant Contextual -->
        <div class="lg:col-span-4 pb-8">
          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant/50 shadow-sm h-[calc(100vh-140px)] sticky top-4 flex flex-col overflow-hidden relative">
            <div class="absolute inset-0 bg-primary/5 pointer-events-none"></div>
            
            <!-- AI Header -->
            <div class="p-4 border-b border-outline-variant/30 bg-white/50 backdrop-blur flex items-center gap-3 relative z-10">
              <div class="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container shadow-sm">
                <span class="material-symbols-outlined">smart_toy</span>
              </div>
              <div>
                <h3 class="font-title-lg text-title-lg text-on-surface">薪资助理</h3>
                <p class="font-label-md text-label-md text-on-surface-variant flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-secondary inline-block"></span>
                  在线支持中
                </p>
              </div>
            </div>
            
            <!-- Chat Canvas -->
            <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-white/30 backdrop-blur relative z-10">
              <!-- System/Agent Message -->
              <div class="flex gap-3">
                <div class="w-8 h-8 rounded-full bg-primary-container flex-shrink-0 flex items-center justify-center text-on-primary-container mt-1">
                  <span class="material-symbols-outlined text-[16px]">smart_toy</span>
                </div>
                <div class="bg-surface-container-low border border-primary/20 rounded-2xl rounded-tl-sm p-3 max-w-[85%] text-body-md text-on-surface">
                  您好，我是您的专属薪资助理。10月份薪资已发放，您本月有 8,000 元的绩效奖金入账，恭喜！<br/><br/>关于本月薪资明细，您有任何疑问吗？
                </div>
              </div>
              
              <!-- Contextual Suggestions -->
              <div class="pl-11 pr-4 flex flex-wrap gap-3">
                <button class="whitespace-nowrap text-xs font-label-md bg-surface-container border border-outline-variant/50 text-on-surface-variant py-1.5 px-3 rounded-full hover:bg-primary/5 hover:border-primary/30 transition-colors">
                  本月个税是怎么扣除的？
                </button>
                <button class="whitespace-nowrap text-xs font-label-md bg-surface-container border border-outline-variant/50 text-on-surface-variant py-1.5 px-3 rounded-full hover:bg-primary/5 hover:border-primary/30 transition-colors">
                  查看专项附加扣除详情
                </button>
                <button class="whitespace-nowrap text-xs font-label-md bg-surface-container border border-outline-variant/50 text-on-surface-variant py-1.5 px-3 rounded-full hover:bg-primary/5 hover:border-primary/30 transition-colors">
                  下载年度薪资证明
                </button>
              </div>
            </div>
            
            <!-- Input Area -->
            <div class="p-4 bg-white border-t border-outline-variant/30 relative z-10">
              <div class="relative flex items-center bg-surface-container-lowest rounded-[16px] border border-outline-variant focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition-all p-1">
                <input 
                  class="flex-1 bg-transparent border-none focus:ring-0 text-body-md px-3 py-2 placeholder-outline-variant outline-none" 
                  placeholder="向 AI 提问关于薪资的细节..." 
                  type="text"
                />
                <button class="w-8 h-8 rounded-full bg-primary text-on-primary flex items-center justify-center hover:bg-primary/90 transition-colors shadow-sm shrink-0">
                  <span class="material-symbols-outlined text-[18px]">arrow_upward</span>
                </button>
              </div>
              <div class="mt-2 text-center">
                <span class="text-[10px] text-outline font-label-md flex items-center justify-center gap-1">
                  <span class="material-symbols-outlined text-[12px]">lock</span>
                  您的对话经企业级加密，安全合规
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
</script>
