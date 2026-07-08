<template>
<div class="min-h-full flex flex-col">
      <div class="max-w-[1440px] mx-auto">
        
        <!-- Header Section -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-lg gap-md">
          <div>
            <div class="flex items-center gap-sm mb-xs">
              <h2 class="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface m-0">Eleanor Vance</h2>
              <span 
                class="font-label-md px-sm py-xs rounded-full flex items-center gap-xs transition-colors duration-200"
                :class="{
                  'bg-secondary-container text-on-secondary-container': status === '最佳匹配',
                  'bg-error/10 text-error': status === '已拒绝',
                  'bg-amber-100 text-amber-800 animate-pulse': status === '安排面试中'
                }"
              >
                <span class="material-symbols-outlined text-[14px]">
                  {{ status === '最佳匹配' ? 'check_circle' : (status === '已拒绝' ? 'cancel' : 'schedule') }}
                </span>
                {{ status }}
              </span>
            </div>
            <p class="font-body-lg text-body-lg text-on-surface-variant">高级 AI 工程师 • 申请职位：首席数据科学家</p>
          </div>
          <div class="flex gap-3 w-full md:w-auto">
            <button 
              class="flex-1 md:flex-none bg-surface-container-lowest border border-outline-variant text-on-surface font-label-md py-2 px-4 rounded-lg hover:bg-surface-container-low transition-colors text-error flex items-center justify-center gap-1"
              :class="{ 'opacity-50 cursor-not-allowed': status !== '最佳匹配' }"
              :disabled="status !== '最佳匹配'"
              @click="handleReject"
            >
              <span class="material-symbols-outlined text-[18px]">close</span> 拒绝
            </button>
            <button 
              class="flex-1 md:flex-none bg-primary text-on-primary font-label-md py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors shadow-sm flex items-center justify-center gap-1"
              :class="{ 'opacity-50 cursor-not-allowed bg-slate-400': status !== '最佳匹配' }"
              :disabled="status !== '最佳匹配'"
              @click="handleScheduleClick"
            >
              安排面试 <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-gutter mb-lg">
          <div class="glass-card rounded-xl p-lg lg:col-span-2">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-md mb-md">
              <div>
                <h3 class="font-title-lg text-title-lg text-on-surface m-0">候选人池</h3>
                <p class="font-body-md text-body-md text-on-surface-variant mt-xs">按岗位匹配度、综合评分和风险标签进行筛选排序。</p>
              </div>
              <div class="flex gap-sm">
                <button class="bg-primary text-on-primary font-label-md py-2 px-4 rounded-lg hover:bg-primary/90 transition-colors">智能筛选</button>
                <button class="bg-surface-container-lowest border border-outline-variant text-primary font-label-md py-2 px-4 rounded-lg hover:bg-surface-container-low transition-colors">一键排序</button>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-sm">
              <article v-for="candidate in rankedCandidates" :key="candidate.name" class="candidate-rank-card">
                <div class="flex justify-between items-start gap-sm">
                  <div>
                    <strong>{{ candidate.name }}</strong>
                    <p>{{ candidate.role }}</p>
                  </div>
                  <span>{{ candidate.score }}</span>
                </div>
                <div class="candidate-rank-card__metrics">
                  <small>匹配度 {{ candidate.match }}</small>
                  <small>{{ candidate.risk }}</small>
                </div>
              </article>
            </div>
          </div>

          <div class="glass-card rounded-xl p-lg">
            <h3 class="font-title-lg text-title-lg text-on-surface m-0 mb-md">智能筛选条件</h3>
            <div class="space-y-sm">
              <div class="flex justify-between text-body-md">
                <span class="text-on-surface-variant">岗位匹配</span>
                <strong class="text-on-surface">首席数据科学家</strong>
              </div>
              <div class="flex justify-between text-body-md">
                <span class="text-on-surface-variant">技能权重</span>
                <strong class="text-on-surface">40%</strong>
              </div>
              <div class="flex justify-between text-body-md">
                <span class="text-on-surface-variant">项目经验</span>
                <strong class="text-on-surface">30%</strong>
              </div>
              <div class="flex justify-between text-body-md">
                <span class="text-on-surface-variant">到岗时间</span>
                <strong class="text-on-surface">7-30 天</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- Bento Grid Layout -->
        <div class="grid grid-cols-1 md:grid-cols-12 gap-gutter">
          
          <!-- Left Column: AI Evaluation & Resume -->
          <div class="md:col-span-8 flex flex-col gap-gutter">
            
            <!-- AI Evaluation Card -->
            <div class="glass-card rounded-xl p-lg ai-glow relative overflow-hidden">
              <div class="absolute top-0 right-0 p-md opacity-10">
                <span class="material-symbols-outlined text-[100px] text-primary">psychology</span>
              </div>
              
              <div class="flex items-center gap-sm mb-md border-b border-outline-variant pb-sm relative z-10">
                <span class="material-symbols-outlined text-primary-container animate-pulse">auto_awesome</span>
                <h3 class="font-title-lg text-title-lg text-on-surface m-0">AI 综合评估</h3>
              </div>
              
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-md relative z-10 mb-md">
                <div class="bg-surface-container-lowest border border-outline-variant rounded-lg p-md text-center">
                  <div class="font-label-md text-on-surface-variant uppercase tracking-wider mb-xs">职位匹配度</div>
                  <div class="font-display text-[40px] leading-none text-primary font-bold">94%</div>
                </div>
                
                <div class="bg-surface-container-lowest border border-outline-variant rounded-lg p-md text-center">
                  <div class="font-label-md text-on-surface-variant uppercase tracking-wider mb-xs">技术熟练度</div>
                  <div class="flex justify-center text-secondary mb-xs">
                    <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">star</span>
                    <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">star</span>
                    <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">star</span>
                    <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">star</span>
                    <span class="material-symbols-outlined" :style="{ fontVariationSettings: '\'FILL\' 1' }">star_half</span>
                  </div>
                  <div class="font-label-md text-on-surface font-semibold">4.8 / 5.0</div>
                </div>
                
                <div class="bg-surface-container-lowest border border-outline-variant rounded-lg p-md text-center">
                  <div class="font-label-md text-on-surface-variant uppercase tracking-wider mb-xs">经验等级</div>
                  <div class="font-headline-md text-headline-md text-on-surface">资深+</div>
                  <div class="font-label-md text-on-surface-variant">8 年经验</div>
                </div>
              </div>
              
              <div class="relative z-10">
                <h4 class="font-label-md text-on-surface-variant uppercase tracking-wider mb-sm">技术栈分析</h4>
                <div class="flex flex-wrap gap-sm">
                  <span class="bg-primary-container/10 border border-primary/20 text-primary font-code-sm px-sm py-xs rounded flex items-center gap-xs">
                    Python <span class="w-2 h-2 rounded-full bg-secondary inline-block"></span>
                  </span>
                  <span class="bg-primary-container/10 border border-primary/20 text-primary font-code-sm px-sm py-xs rounded flex items-center gap-xs">
                    多智能体协作 <span class="w-2 h-2 rounded-full bg-secondary inline-block"></span>
                  </span>
                  <span class="bg-primary-container/10 border border-primary/20 text-primary font-code-sm px-sm py-xs rounded flex items-center gap-xs">
                    知识检索架构 <span class="w-2 h-2 rounded-full bg-secondary inline-block"></span>
                  </span>
                  <span class="bg-surface-container-low border border-outline-variant text-on-surface-variant font-code-sm px-sm py-xs rounded flex items-center gap-xs">
                    PyTorch <span class="w-2 h-2 rounded-full bg-surface-dim inline-block"></span>
                  </span>
                  <span class="bg-surface-container-low border border-outline-variant text-on-surface-variant font-code-sm px-sm py-xs rounded flex items-center gap-xs">
                    Docker <span class="w-2 h-2 rounded-full bg-surface-dim inline-block"></span>
                  </span>
                </div>
              </div>
            </div>

            <!-- Resume Preview -->
            <div class="glass-card rounded-xl p-lg flex-1 flex flex-col min-h-[400px]">
              <div class="flex justify-between items-center mb-md pb-sm border-b border-outline-variant">
                <h3 class="font-title-lg text-title-lg text-on-surface m-0 flex items-center gap-sm">
                  <span class="material-symbols-outlined text-on-surface-variant">description</span> 原始简历预览
                </h3>
                <button class="text-primary font-label-md hover:underline flex items-center gap-xs">
                  <span class="material-symbols-outlined text-[16px]">open_in_new</span> 查看完整版
                </button>
              </div>
              <div class="bg-surface-container-lowest border border-outline-variant rounded p-md flex-1 overflow-y-auto relative">
                <div class="absolute inset-0 bg-gradient-to-b from-transparent to-surface-container-lowest pointer-events-none flex items-end justify-center pb-md z-10">
                  <button class="bg-surface-container border border-outline-variant text-on-surface font-label-md py-xs px-md rounded shadow-sm hover:bg-surface-container-high transition-colors pointer-events-auto">
                    向下滑动阅读更多
                  </button>
                </div>
                <div class="font-code-sm text-on-surface-variant whitespace-pre-wrap blur-[1px] opacity-70">
Eleanor Vance
San Francisco, CA | el.vance@email.com | linkedin.com/in/eleanorvance

职业总结
首席数据科学家，拥有 8 年以上自然语言处理和生成式智能应用经验。在设计和部署可扩展知识检索架构方面有良好记录，可将企业数据检索效率提高 40% 以上。热衷于可信智能系统实施和构建稳健的任务编排框架。

工作经历
高级 AI 工程师 | TechNova Solutions | 2021 - 至今
- 使用智能任务编排架构并实现多角色协作系统，将客户服务升级率降低了 25%。
- 领导 4 名 ML 工程师团队开发专有的知识检索流水线，每日处理超过 5000 万份文档。
- 通过提示工程和模型量化技术将 LLM 推理成本优化了 30%。

数据科学家 | DataCore Analytics | 2018 - 2021
- 为客户流失开发预测模型...
                </div>
              </div>
            </div>
            
          </div>

          <!-- Right Column: Summary & Actions -->
          <div class="md:col-span-4 flex flex-col gap-gutter">
            
            <!-- AI Insights -->
            <div class="glass-card rounded-xl p-lg border-t-4 border-t-primary">
              <h3 class="font-title-lg text-title-lg text-on-surface m-0 mb-md flex items-center gap-sm">
                <span class="material-symbols-outlined text-primary">insights</span> 智能分析总结
              </h3>
              
              <div class="mb-md">
                <h4 class="font-label-md text-on-surface-variant uppercase tracking-wider mb-xs flex items-center gap-xs">
                  <span class="material-symbols-outlined text-secondary text-[16px]">thumb_up</span> 优势
                </h4>
                <ul class="list-disc list-inside font-body-md text-on-surface space-y-xs ml-xs">
                  <li>在多智能体协作系统方面有卓越背景。</li>
                  <li>具备出色的团队领导经验（曾管理 4 名工程师）。</li>
                  <li>高度关注生产环境中的成本优化。</li>
                </ul>
              </div>
              
              <div class="mb-md">
                <h4 class="font-label-md text-on-surface-variant uppercase tracking-wider mb-xs flex items-center gap-xs">
                  <span class="material-symbols-outlined text-error text-[16px]">warning</span> 潜在风险
                </h4>
                <ul class="list-disc list-inside font-body-md text-on-surface space-y-xs ml-xs">
                  <li>缺乏对本公司特定云平台（Azure）的直接经验，但技术底层可迁移。</li>
                  <li>目前职位的在职时间略短于首席职位的平均水平。</li>
                </ul>
              </div>
              
              <button class="w-full bg-gradient-to-r from-primary to-tertiary text-on-primary font-label-md py-sm px-md rounded-lg mt-sm shadow-md hover:opacity-90 transition-opacity flex items-center justify-center gap-sm">
                <span class="material-symbols-outlined text-[18px]">chat</span> 查看评估依据
              </button>
            </div>

            <!-- Quick Details -->
            <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg">
              <h3 class="font-title-lg text-title-lg text-on-surface m-0 mb-md">候选人详情</h3>
              <dl class="space-y-sm font-body-md">
                <div class="flex justify-between border-b border-surface-variant pb-xs">
                  <dt class="text-on-surface-variant">所在地</dt>
                  <dd class="text-on-surface font-medium">旧金山, CA (可远程工作)</dd>
                </div>
                <div class="flex justify-between border-b border-surface-variant pb-xs">
                  <dt class="text-on-surface-variant">期望薪资</dt>
                  <dd class="text-on-surface font-medium">$180k - $210k</dd>
                </div>
                <div class="flex justify-between border-b border-surface-variant pb-xs">
                  <dt class="text-on-surface-variant">到岗时间</dt>
                  <dd class="text-on-surface font-medium">4 周</dd>
                </div>
                <div class="flex justify-between pb-xs">
                  <dt class="text-on-surface-variant">来源</dt>
                  <dd class="text-on-surface font-medium">直接申请</dd>
                </div>
              </dl>
            </div>
            
          </div>
        </div>
      </div>
    </div>

  <!-- Schedule Interview Modal -->
  <div v-if="showModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl border border-outline-variant/30 shadow-2xl overflow-hidden shrink-0" style="width: 448px; max-width: 90vw;">
        <!-- Modal Header -->
        <div class="px-6 py-4 border-b border-outline-variant/30 bg-surface-container-low flex justify-between items-center">
          <h3 class="font-title-lg text-[18px] font-bold text-on-surface flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">calendar_month</span>
            安排面试排期
          </h3>
          <button @click="showModal = false" class="text-outline-variant hover:text-on-surface transition-colors flex items-center justify-center">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <!-- Modal Body -->
        <div class="p-6 space-y-4">
          <div>
            <label class="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider block mb-1">候选人</label>
            <div class="text-sm font-semibold text-on-surface">Eleanor Vance (首席数据科学家申请者)</div>
          </div>

          <!-- Slots Select -->
          <div>
            <label class="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider block mb-2">选择面试时间段（系统推荐）</label>
            <div class="space-y-2">
              <label class="flex items-center justify-between p-3 rounded-lg border border-outline-variant/60 cursor-pointer hover:bg-primary/5 hover:border-primary/40 transition-colors" :class="{ 'border-primary bg-primary/5': selectedSlot === 'slot1' }">
                <div class="flex items-center gap-2">
                  <input type="radio" v-model="selectedSlot" value="slot1" class="text-primary focus:ring-primary w-4 h-4 cursor-pointer" />
                  <span class="text-xs text-on-surface font-medium">明天 (周三) 10:00 - 11:00 AM</span>
                </div>
                <span class="text-[10px] text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded font-bold">空闲</span>
              </label>
              <label class="flex items-center justify-between p-3 rounded-lg border border-outline-variant/60 cursor-pointer hover:bg-primary/5 hover:border-primary/40 transition-colors" :class="{ 'border-primary bg-primary/5': selectedSlot === 'slot2' }">
                <div class="flex items-center gap-2">
                  <input type="radio" v-model="selectedSlot" value="slot2" class="text-primary focus:ring-primary w-4 h-4 cursor-pointer" />
                  <span class="text-xs text-on-surface font-medium">明天 (周三) 02:30 - 03:30 PM</span>
                </div>
                <span class="text-[10px] text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded font-bold">空闲</span>
              </label>
              <label class="flex items-center justify-between p-3 rounded-lg border border-outline-variant/60 cursor-pointer hover:bg-primary/5 hover:border-primary/40 transition-colors" :class="{ 'border-primary bg-primary/5': selectedSlot === 'slot3' }">
                <div class="flex items-center gap-2">
                  <input type="radio" v-model="selectedSlot" value="slot3" class="text-primary focus:ring-primary w-4 h-4 cursor-pointer" />
                  <span class="text-xs text-on-surface font-medium">本周四 09:30 - 10:30 AM</span>
                </div>
                <span class="text-[10px] text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded font-bold">空闲</span>
              </label>
            </div>
          </div>

          <!-- Interviewer Select -->
          <div>
            <label class="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider block mb-1">指定面试官</label>
            <select v-model="selectedInterviewer" class="w-full px-3 py-2 bg-surface-container-low border border-outline-variant rounded-lg text-xs outline-none focus:border-primary text-on-surface">
              <option>王刚 (技术面试官)</option>
              <option>林雨晴 (HR 专员)</option>
              <option>张伟 (高级工程师)</option>
            </select>
          </div>

          <!-- Format Select -->
          <div>
            <label class="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider block mb-1">面试形式</label>
            <select v-model="selectedFormat" class="w-full px-3 py-2 bg-surface-container-low border border-outline-variant rounded-lg text-xs outline-none focus:border-primary text-on-surface">
              <option>线上 - AI 面试间</option>
              <option>腾讯会议 / Zoom</option>
              <option>线下 - A栋4楼会议室</option>
            </select>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="px-6 py-4 border-t border-outline-variant/30 bg-surface-container-low flex justify-end gap-3">
          <button @click="showModal = false" class="px-4 py-2 bg-white border border-outline-variant rounded-lg font-medium text-xs text-on-surface-variant hover:bg-surface-container-low transition-colors">
            取消
          </button>
          <button @click="confirmSchedule" class="px-4 py-2 bg-primary text-on-primary rounded-lg font-semibold text-xs hover:bg-primary/95 transition-colors shadow-sm">
            确认预约
          </button>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const emit = defineEmits<{
  navigate: [view: string];
  'show-toast': [message: string];
}>();

const status = ref<'最佳匹配' | '已拒绝' | '安排面试中'>('最佳匹配');

// Modal State
const showModal = ref(false);
const selectedSlot = ref('slot1');
const selectedInterviewer = ref('王刚 (技术面试官)');

const rankedCandidates = [
  { name: 'Eleanor Vance', role: '首席数据科学家', score: '94', match: '94%', risk: '低风险' },
  { name: 'Michael Chen', role: '高级前端工程师', score: '89', match: '91%', risk: '需复核到岗时间' },
  { name: 'Sarah Jenkins', role: '产品经理', score: '86', match: '88%', risk: '薪资期望偏高' }
];
const selectedFormat = ref('线上 - AI 面试间');

function handleReject() {
  if (status.value === '已拒绝') return;
  status.value = '已拒绝';
  emit('show-toast', '已成功将候选人 Eleanor Vance 移出匹配池。自动下发谢绝信邮件。');
}

function handleScheduleClick() {
  if (status.value === '安排面试中') return;
  showModal.value = true;
}

function confirmSchedule() {
  showModal.value = false;
  status.value = '安排面试中';
  
  let timeStr = '明天 10:00 AM';
  if (selectedSlot.value === 'slot2') timeStr = '明天 02:30 PM';
  if (selectedSlot.value === 'slot3') timeStr = '本周四 09:30 AM';
  
  emit('show-toast', `已预定面试时间：${timeStr}！已自动向候选人与 ${selectedInterviewer.value} 推送日程通知。`);
  
  setTimeout(() => {
    emit('navigate', 'interviews');
  }, 1500);
}
</script>

<style scoped>
.candidate-rank-card {
  display: grid;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  background: var(--color-surface-soft);
}

.candidate-rank-card strong {
  display: block;
  color: var(--color-text);
}

.candidate-rank-card p {
  margin: 4px 0 0;
  color: var(--color-muted);
  font-size: 12px;
}

.candidate-rank-card > div:first-child > span {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-weight: 800;
}

.candidate-rank-card__metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.candidate-rank-card__metrics small {
  padding: 5px 8px;
  border-radius: 999px;
  background: #fff;
  color: var(--color-muted);
  font-weight: 700;
}
</style>
