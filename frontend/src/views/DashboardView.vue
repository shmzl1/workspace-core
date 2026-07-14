<template>
<div class="min-h-full flex flex-col">
      <div class="mb-6 flex justify-between items-end">
        <div>
          <h2 class="text-3xl font-bold text-on-surface mb-1">智能招聘看板</h2>
          <p class="text-on-surface-variant">企业级 HR 智能助手概览</p>
        </div>
        <button class="px-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg text-primary-container font-medium hover:bg-surface-container-low transition-colors flex items-center gap-2 shadow-sm">
          <span class="material-symbols-outlined text-[18px]">download</span>
          导出报表
        </button>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-12 gap-6 mb-6">
        <!-- Metric Cards (8 cols) -->
        <div class="xl:col-span-8 flex gap-6">
          <div class="flex-1 bg-surface-container-lowest rounded-xl p-6 border border-outline-variant shadow-sm relative overflow-hidden group">
            <div class="flex justify-between items-start mb-4">
              <div class="p-2 bg-primary-container/10 rounded-lg text-primary-container">
                <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">description</span>
              </div>
              <span class="text-sm font-medium text-secondary bg-secondary/10 px-2 py-1 rounded-full">+14%</span>
            </div>
            <div class="flex items-end justify-between">
              <div>
                <div class="text-3xl font-bold text-on-surface mb-1">12</div>
                <div class="text-sm text-on-surface-variant font-medium">新增简历</div>
              </div>
            </div>
          </div>

          <div class="flex-1 bg-surface-container-lowest rounded-xl p-6 ai-gradient-border shadow-sm relative overflow-hidden ai-glow">
            <div class="absolute -bottom-10 -right-10 w-40 h-40 bg-primary-container/10 blur-2xl rounded-full z-0" />
            <div class="relative z-10">
              <div class="flex justify-between items-start mb-4">
                <div class="p-2 bg-surface rounded-lg text-primary-container border border-outline-variant relative">
                  <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">smart_toy</span>
                  <div class="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-500 rounded-full pulse-dot" />
                </div>
                <span class="text-xs font-medium text-primary bg-primary-container/10 px-2 py-1 rounded-full flex items-center gap-1">
                  <span class="material-symbols-outlined text-[14px]">auto_awesome</span> 活跃中
                </span>
              </div>
              <div class="flex items-end justify-between">
                <div>
                  <div class="text-3xl font-bold text-on-surface mb-1">5</div>
                  <div class="text-sm text-on-surface-variant font-medium">AI 筛选完成</div>
                </div>
                <div class="h-10 w-10 relative flex items-center justify-center">
                  <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="16" fill="none" class="text-surface-variant" stroke="currentColor" strokeWidth="3" />
                    <circle cx="18" cy="18" r="16" fill="none" class="text-primary-container" stroke="currentColor" strokeWidth="3" strokeDasharray="100 100" strokeDashoffset="25" />
                  </svg>
                  <span class="absolute text-[10px] font-bold text-primary-container">75%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex-1 bg-surface-container-lowest rounded-xl p-6 border border-outline-variant shadow-sm relative overflow-hidden">
            <div class="flex justify-between items-start mb-4">
              <div class="p-2 bg-surface-container-high rounded-lg text-on-surface-variant">
                <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">check_circle</span>
              </div>
            </div>
            <div class="flex items-end justify-between">
              <div>
                <div class="text-3xl font-bold text-on-surface mb-1">3</div>
                <div class="text-sm text-on-surface-variant font-medium">进入面试阶段</div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Processing Center (4 cols) -->
        <div class="xl:col-span-4 bg-[#0A0F1C] rounded-xl border border-primary/20 shadow-[0_0_15px_rgba(27,77,255,0.15)] relative overflow-hidden flex flex-col min-h-[180px]">
          <div class="p-4 border-b border-white/10 flex justify-between items-center relative z-10">
            <h3 class="font-semibold text-white flex items-center gap-2">
              <span class="material-symbols-outlined text-primary-fixed text-[18px]">account_tree</span>
              智能分析链路
            </h3>
            <div class="flex items-center gap-1.5">
              <div class="w-2 h-2 rounded-full bg-emerald-500 pulse-dot" />
              <span class="font-mono text-[11px] text-emerald-500">实时</span>
            </div>
          </div>
          <div class="p-4 flex-1 relative z-10 flex flex-col justify-center">
            <div class="flex justify-between items-center mb-4">
              <div class="text-center">
                <div class="text-xs text-white/70 mb-1">知识检索</div>
                <div class="text-xl font-bold text-white">4.2ms</div>
              </div>
              <div class="flex-1 px-4 relative h-4">
                <svg class="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 20">
                  <path d="M0 10 Q 25 20, 50 10 T 100 10" fill="none" stroke="rgba(185, 195, 255, 0.5)" strokeWidth="2" class="graph-line" />
                  <circle cx="50" cy="10" r="3" fill="#b9c3ff">
                    <animate attributeName="r" values="2;4;2" dur="1s" repeatCount="indefinite" />
                  </circle>
                </svg>
              </div>
              <div class="text-center">
                <div class="text-xs text-white/70 mb-1">综合分析</div>
                <div class="text-xl font-bold text-primary-fixed">1.8s</div>
              </div>
            </div>
            <div class="font-mono text-xs text-white/50 truncate">
              <span class="text-primary-fixed mr-1">&gt;</span>
              正在查询候选人 "React.js" 相关技能知识图谱...
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <!-- Pipeline view (8 cols) -->
        <div class="xl:col-span-8 bg-surface-container-lowest rounded-xl border border-outline-variant shadow-sm overflow-hidden flex flex-col h-[500px]">
          <div class="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-low/50">
            <h3 class="font-semibold text-on-surface flex items-center gap-2">
              AI 筛选流水线
              <span class="bg-primary-container/10 text-primary-container text-xs px-2 py-0.5 rounded-full flex items-center gap-1">
                <span class="material-symbols-outlined text-[12px]">auto_awesome</span> 智能排序
              </span>
            </h3>
            <div class="flex gap-2">
              <button class="px-3 py-1 bg-surface border border-outline-variant rounded-md text-on-surface-variant text-xs hover:bg-surface-container-low transition-colors">网格视图</button>
              <button class="px-3 py-1 bg-primary text-white rounded-md text-xs shadow-sm">流水线视图</button>
            </div>
          </div>
          
          <div class="flex-1 p-6 relative bg-surface-bright overflow-hidden">
            <!-- Grid Background -->
            <div 
              class="absolute inset-0 opacity-40" 
              :style="{
                backgroundImage: 'linear-gradient(to right, rgba(0,0,0,0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(0,0,0,0.05) 1px, transparent 1px)',
                backgroundSize: '40px 40px'
              }"
            />
            
            <div class="absolute inset-0 flex">
              <!-- Column 1: Extract -->
              <div class="flex-1 border-r border-outline-variant/30 flex flex-col pt-4 px-4 relative">
                <div class="text-center text-xs font-medium text-on-surface-variant mb-6 bg-surface-container px-2 py-1 rounded mx-auto border border-outline-variant/50">原始提取</div>
                
                <div class="bg-surface-container-lowest p-3 rounded-lg border border-outline-variant shadow-sm relative z-10 flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-surface-variant text-on-surface-variant flex items-center justify-center font-bold text-[10px]">AL</div>
                  <div>
                    <div class="text-sm font-medium">Alex Lee</div>
                    <div class="font-mono text-[10px] text-on-surface-variant mt-0.5">正在解析 PDF...</div>
                  </div>
                  <div class="absolute -right-[5px] top-1/2 -translate-y-1/2 w-2 h-2 bg-outline rounded-full" />
                </div>
              </div>

              <!-- Column 2: Semantic Match -->
              <div class="flex-1 border-r border-outline-variant/30 flex flex-col pt-4 px-4 relative">
                <div class="text-center text-xs font-medium text-primary mb-6 bg-primary-container/10 px-2 py-1 rounded mx-auto border border-primary-container/30">语义匹配</div>
                
                <div class="bg-surface-container-lowest p-3 rounded-lg border-2 border-primary/20 shadow-sm relative z-10 flex flex-col gap-2 mt-8 ai-glow animate-pulse" :style="{ animationDuration: '3s' }">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-surface-container-high overflow-hidden">
                      <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuC4JExOfEgKff3_zwoGHO_pX6WwAtseY2QgK0RvTHNYWUsvKJmv6cAWDWum2grupoInSyKOzqLPOfW6i6kwr7OsmCUeHsf9Sfg1uLAAcaGfj07hyhmJ8-_Nm0JqC1uu2zqN4ZL0b6aK749jS3D78k994GK4Z8z-RoAKKNTpgoO8_PYi43Fg0luUQnp_7k2vGehUnxTyhH0I83dAm6GQUiidXYIOhsuMlawSLNCWgg9ec98QiM__mT-EGYr0VBHvsop13Tpx93AS0PF0" alt="Candidate" class="w-full h-full object-cover"/>
                    </div>
                    <div>
                      <div class="text-sm font-medium">Michael Chen</div>
                      <div class="font-mono text-[10px] text-primary flex items-center gap-1 mt-0.5">
                        <span class="material-symbols-outlined text-[10px]">sync</span> 技能匹配中
                      </div>
                    </div>
                  </div>
                  <div class="w-full h-1 bg-surface-variant rounded-full overflow-hidden mt-1">
                    <div class="bg-primary h-full w-[60%]" />
                  </div>
                  <div class="absolute -left-[5px] top-[25px] w-2 h-2 bg-primary rounded-full" />
                  <div class="absolute -right-[5px] top-[25px] w-2 h-2 bg-primary rounded-full" />
                </div>
              </div>

              <!-- Column 3: Top Match -->
              <div class="flex-1 flex flex-col pt-4 px-4 relative overflow-visible">
                <div class="text-center text-xs font-medium text-emerald-600 mb-6 bg-emerald-50 px-2 py-1 rounded mx-auto border border-emerald-200 flex items-center gap-1 justify-center">
                  <span class="material-symbols-outlined text-[14px]">star</span> 顶级匹配
                </div>
                
                <div class="bg-gradient-to-br from-surface-container-lowest to-emerald-50/50 p-4 rounded-xl border-2 border-emerald-500 shadow-[0_4px_15px_rgba(16,185,129,0.15)] relative z-10 mt-[100px]">
                  <div class="absolute -top-3 -right-3 bg-emerald-500 text-white font-bold text-[10px] px-2 py-1 rounded-full shadow-md">98% 匹配</div>
                  <div class="flex items-center gap-3 mb-3">
                    <div class="w-10 h-10 rounded-full bg-surface-container-high overflow-hidden border-2 border-white shadow-sm">
                      <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCqIdeYoUoP8sarJdKwmHtiA9UQzmDixIyTog_YcUTwc8-iKkeUXt10NNk2K3n9ACr0Xd5nTwadoxKZH_VUBneq64ptKkkWL6fNFcc0ZZgOnpjZICAoMS7vsg_10BafF5VkpyKi1q3IaCZJLj3y5BW4ldbjgDJ0xqwlWqzLV_vd92HF61y9w9UQWwKJQofzLa6IXxzvqD7Mjel_Rtd8Za4t6B_CjXJncEAcbzg8Mnmv0GRdtkdUGVgguCPhsPZhkuQKKEMy4eOOPCZe" alt="Candidate" class="w-full h-full object-cover"/>
                    </div>
                    <div>
                      <div class="text-sm font-bold text-on-surface">Sarah Jenkins</div>
                      <div class="text-xs text-on-surface-variant">高级前端工程师</div>
                    </div>
                  </div>
                  <div class="flex gap-1.5 flex-wrap">
                    <span class="text-[10px] bg-surface-variant px-1.5 py-0.5 rounded text-on-surface-variant font-medium">React</span>
                    <span class="text-[10px] bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded font-medium border border-emerald-200">领导力</span>
                    <span class="text-[10px] bg-surface-variant px-1.5 py-0.5 rounded text-on-surface-variant font-medium">系统设计</span>
                  </div>
                  <div class="absolute -left-[5px] top-[30px] w-2 h-2 bg-emerald-500 rounded-full" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Schedule (4 cols) -->
        <div class="xl:col-span-4 bg-surface-container-lowest rounded-xl border border-outline-variant shadow-sm flex flex-col h-[500px]">
          <div class="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-low/50 rounded-t-xl">
            <h3 class="font-semibold text-on-surface">每周日程</h3>
            <button class="text-on-surface-variant hover:text-primary transition-colors">
              <span class="material-symbols-outlined">more_horiz</span>
            </button>
          </div>
          
          <div class="p-4 flex-1 overflow-y-auto space-y-4">
            <div class="flex gap-3 items-start group">
              <div class="w-12 text-center pt-1">
                <div class="text-[10px] font-medium text-on-surface-variant uppercase">周一</div>
                <div class="text-xl font-bold text-on-surface">14</div>
              </div>
              <div class="flex-1 bg-surface rounded-lg p-3 border border-outline-variant group-hover:border-primary/30 transition-colors">
                <div class="flex justify-between items-start mb-1">
                  <div class="text-sm font-semibold text-on-surface">Sarah Jenkins</div>
                  <div class="text-[10px] font-medium text-primary bg-primary-container/10 px-1.5 py-0.5 rounded">10:00 AM</div>
                </div>
                <div class="text-xs text-on-surface-variant">高级前端工程师</div>
              </div>
            </div>

            <div class="flex gap-3 items-start group">
              <div class="w-12 text-center pt-1">
                <div class="text-[10px] font-medium text-on-surface-variant uppercase">周二</div>
                <div class="text-xl font-bold text-on-surface">15</div>
              </div>
              <div class="flex-1 bg-surface-container-lowest border border-primary-container/30 rounded-lg p-3 ai-glow relative overflow-hidden group-hover:border-primary-container/50 transition-colors">
                <div class="absolute left-0 top-0 bottom-0 w-1 bg-primary-container" />
                <div class="flex justify-between items-start mb-1 pl-1">
                  <div class="text-sm font-semibold text-on-surface flex items-center gap-1">
                    Michael Chen
                    <span class="material-symbols-outlined text-[14px] text-primary-container">smart_toy</span>
                  </div>
                  <div class="text-[10px] font-medium text-primary bg-primary-container/10 px-1.5 py-0.5 rounded">2:30 PM</div>
                </div>
                <div class="text-xs text-on-surface-variant pl-1">产品经理</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <section class="mt-6 bg-surface-container-lowest rounded-xl border border-outline-variant shadow-sm overflow-hidden">
        <div class="p-5 border-b border-outline-variant flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-surface-container-low/50">
          <div>
            <h3 class="font-semibold text-on-surface flex items-center gap-2">
              <span class="material-symbols-outlined text-primary-container">payments</span>
              薪资预审与风险提示
            </h3>
            <p class="text-sm text-on-surface-variant mt-1">汇总待预审批次、异常薪资项、权限风险与 HR 审批建议。</p>
          </div>
          <div class="flex gap-2">
            <button
              class="px-3 py-2 bg-primary text-white rounded-lg text-sm font-semibold hover:bg-primary/90 transition-colors flex items-center gap-1"
              @click="openPayrollReview"
            >
              <span class="material-symbols-outlined text-[16px]">visibility</span>
              查看预审详情
            </button>
            <button
              class="px-3 py-2 border border-outline-variant rounded-lg text-sm font-semibold text-on-surface hover:bg-surface-container-low transition-colors flex items-center gap-1"
              :class="{ 'bg-secondary/10 text-secondary border-secondary/20': payrollHandled }"
              @click="markPayrollHandled"
            >
              <span class="material-symbols-outlined text-[16px]">{{ payrollHandled ? 'check_circle' : 'task_alt' }}</span>
              {{ payrollHandled ? '已标记处理' : '标记已处理' }}
            </button>
          </div>
        </div>

        <div v-if="payrollNotice" class="mx-5 mt-5 rounded-lg bg-[#F7F9FF] border border-primary-container/20 p-3 flex gap-2 text-sm text-on-surface-variant">
          <span class="material-symbols-outlined text-primary-container text-[18px]">info</span>
          <span>{{ payrollNotice }}</span>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-5 gap-4 p-5">
          <article
            v-for="item in payrollReviewCards"
            :key="item.label"
            class="bg-surface rounded-lg border border-outline-variant p-4"
          >
            <div class="flex items-center justify-between mb-3">
              <span class="material-symbols-outlined text-primary-container">{{ item.icon }}</span>
              <strong class="text-xl text-on-surface">{{ item.value }}</strong>
            </div>
            <h4 class="text-sm font-semibold text-on-surface mb-1">{{ item.label }}</h4>
            <p class="text-xs text-on-surface-variant leading-relaxed">{{ item.description }}</p>
          </article>
        </div>

        <div class="mx-5 mb-5 rounded-lg bg-[#F8FAFC] border border-outline-variant p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div>
            <h4 class="text-sm font-semibold text-on-surface mb-1">HR 审批建议</h4>
            <p class="text-sm text-on-surface-variant">
              {{ approvalSuggestion }}
            </p>
          </div>
          <span
            class="text-xs font-bold px-3 py-1 rounded-full"
            :class="payrollHandled ? 'bg-secondary/10 text-secondary' : 'bg-[#FFF7ED] text-[#EA580C]'"
          >
            {{ payrollHandled ? '风险已记录' : riskStatusLabel }}
          </span>
        </div>
      </section>
      
      <!-- Floating Action / Assistant Input -->
      <div class="mt-8 flex justify-center sticky bottom-8 z-40">
        <div class="w-full max-w-3xl relative group">
          <div class="absolute -inset-1 bg-gradient-to-r from-primary-container to-tertiary-container rounded-[20px] blur opacity-20 group-hover:opacity-40 transition duration-500" />
          <div class="relative flex items-center bg-surface-container-lowest rounded-[16px] border border-outline-variant p-2 shadow-lg">
            <button class="p-2 text-primary-container hover:bg-primary-container/10 rounded-full transition-colors flex-shrink-0">
              <span class="material-symbols-outlined">auto_awesome</span>
            </button>
            <input 
              type="text" 
              placeholder="让智能助手筛选候选人、安排面试或生成报表..." 
              class="flex-1 bg-transparent border-none focus:ring-0 text-sm px-2 text-on-surface placeholder:text-outline"
            />
            <button class="w-10 h-10 bg-primary text-white rounded-full hover:bg-primary/90 transition-colors flex items-center justify-center flex-shrink-0 ml-2 shadow-sm">
              <span class="material-symbols-outlined text-[18px] ml-0.5">send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { reviewPayrollPreAudit } from '../shared/api/modules';

const emit = defineEmits<{
  'show-toast': [message: string];
}>();

const payrollHandled = ref(false);
const payrollNotice = ref('');
const approvalSuggestion = ref('优先复核绩效奖金与异常扣款来源，确认薪酬管理员访问范围后再提交审批。');
const riskStatusLabel = ref('等待 HR 复核');

const payrollReviewCards = ref([
  {
    label: '待预审批次',
    value: '3',
    icon: 'pending_actions',
    description: '本周薪资批次中仍有 3 个批次等待 HR 复核。'
  },
  {
    label: '异常薪资项',
    value: '5',
    icon: 'report',
    description: '包含绩效奖金、补贴调整和扣款金额波动。'
  },
  {
    label: '权限风险',
    value: '2',
    icon: 'admin_panel_settings',
    description: '检测到跨部门薪资查看申请，需要补充审批理由。'
  },
  {
    label: '扣款来源说明',
    value: '4',
    icon: 'receipt_long',
    description: '考勤扣款、社保补缴和福利抵扣需要逐项确认。'
  },
  {
    label: '审批建议',
    value: '复核',
    icon: 'gavel',
    description: '建议先处理高风险访问记录，再提交薪资批次。'
  }
]);

async function openPayrollReview() {
  payrollNotice.value = '';
  try {
    const result = await reviewPayrollPreAudit({
      requester_role: 'HR_SPECIALIST',
      requester_employee_id: 1,
      include_line_items: true
    });

    if (result.status === 'algorithm_not_ready') {
      payrollNotice.value = result.message;
      payrollReviewCards.value[0].value = String(result.pending_batches ?? payrollReviewCards.value[0].value);
      emit('show-toast', result.message);
      return;
    }

    payrollReviewCards.value[0].value = String(result.pending_batches);
    payrollReviewCards.value[1].value = String(result.abnormal_salary_items.length);
    payrollReviewCards.value[2].value = String(result.permission_risks.length);
    payrollReviewCards.value[3].value = String(result.deduction_sources.length);
    payrollReviewCards.value[4].value = result.risk_level ?? '复核';
    approvalSuggestion.value = result.approval_suggestion ?? approvalSuggestion.value;
    riskStatusLabel.value = result.risk_level ? `风险等级：${result.risk_level}` : '等待 HR 复核';
    emit('show-toast', '薪资预审详情已刷新。');
  } catch {
    payrollNotice.value = '薪资预审服务暂时不可用，请稍后重试。';
    emit('show-toast', payrollNotice.value);
  }
}

function markPayrollHandled() {
  payrollHandled.value = true;
  emit('show-toast', '薪资预审风险已标记为已处理。');
}
</script>

<style scoped>
/* 深色模式适配 */
[data-theme="dark"] .bg-emerald-50 { background-color: #052e15 !important; }
[data-theme="dark"] .text-emerald-600 { color: #86efab !important; }
[data-theme="dark"] .bg-emerald-100 { background-color: #064e3b !important; }
[data-theme="dark"] .text-emerald-700 { color: #6ee7b8 !important; }
[data-theme="dark"] .to-emerald-50\/50 { --tw-gradient-to: rgba(5, 46, 22, 0.5) !important; }
[data-theme="dark"] .bg-\[\#F7F9FF\] { background-color: #1a2333 !important; }
[data-theme="dark"] .bg-\[\#F8FAFC\] { background-color: #1e293c !important; }
[data-theme="dark"] .bg-\[\#FFF7ED\] { background-color: #451a02 !important; }
[data-theme="dark"] .text-\[\#EA580C\] { color: #fdba75 !important; }
</style>
