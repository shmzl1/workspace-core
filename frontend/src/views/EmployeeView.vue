<template>
<div class="min-h-full flex flex-col">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h2 class="text-3xl font-bold text-on-surface">员工管理</h2>
          <p class="text-sm text-on-surface-variant mt-1">管理员工目录和状态</p>
        </div>
        <div class="flex items-center gap-2">
          <button class="px-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm font-medium text-on-surface hover:bg-surface-container-low transition-colors flex items-center gap-2">
            <span class="material-symbols-outlined text-[18px]">upload</span> 导入
          </button>
          <button class="px-4 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm font-medium text-on-surface hover:bg-surface-container-low transition-colors flex items-center gap-2">
            <span class="material-symbols-outlined text-[18px]">download</span> 导出
          </button>
          <button class="px-4 py-2 bg-primary rounded-lg text-sm font-medium text-white hover:bg-primary/90 transition-colors flex items-center gap-2 shadow-sm">
            <span class="material-symbols-outlined text-[18px]">person_add</span> 添加员工
          </button>
        </div>
      </div>

      <!-- KPI Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-medium text-on-surface-variant uppercase tracking-wider">总人数</span>
            <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <span class="material-symbols-outlined text-[18px]">groups</span>
            </div>
          </div>
          <div>
            <span class="text-4xl font-bold text-on-surface">1,248</span>
            <div class="flex items-center gap-1 mt-1 text-secondary text-xs font-medium">
              <span class="material-symbols-outlined text-[16px]">trending_up</span> 较上月 +2.4%
            </div>
          </div>
        </div>
        
        <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-medium text-on-surface-variant uppercase tracking-wider">新入职 (本月)</span>
            <div class="w-8 h-8 rounded-full bg-secondary/10 flex items-center justify-center text-secondary">
              <span class="material-symbols-outlined text-[18px]">how_to_reg</span>
            </div>
          </div>
          <div>
            <span class="text-4xl font-bold text-on-surface">32</span>
            <div class="flex items-center gap-1 mt-1 text-on-surface-variant text-xs font-medium">
              14 人正在入职
            </div>
          </div>
        </div>

        <div class="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-medium text-on-surface-variant uppercase tracking-wider">离职 (本月)</span>
            <div class="w-8 h-8 rounded-full bg-error/10 flex items-center justify-center text-error">
              <span class="material-symbols-outlined text-[18px]">person_remove</span>
            </div>
          </div>
          <div>
            <span class="text-4xl font-bold text-on-surface">8</span>
            <div class="flex items-center gap-1 mt-1 text-secondary text-xs font-medium">
              <span class="material-symbols-outlined text-[16px]">trending_down</span> 较上月 -1.2%
            </div>
          </div>
        </div>

        <div class="bg-surface-container-lowest border border-primary/30 rounded-xl p-5 shadow-[0_4px_15px_rgba(27,77,255,0.1)] relative overflow-hidden flex flex-col justify-between ai-glow">
          <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-50" />
          <div class="relative z-10 flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-primary uppercase tracking-wider">满意度指数</span>
            <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary relative">
              <span class="material-symbols-outlined text-[18px]">auto_awesome</span>
              <span class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-secondary animate-pulse" />
            </div>
          </div>
          <div class="relative z-10">
            <div class="flex items-baseline gap-1">
              <span class="text-4xl font-bold text-on-surface">8.6</span>
              <span class="text-sm text-on-surface-variant">/ 10</span>
            </div>
            <div class="flex items-center gap-1 mt-1 text-primary text-xs font-bold cursor-pointer hover:underline">
              查看 AI 情绪分析 <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Table Section -->
      <div class="bg-surface-container-lowest border border-outline-variant rounded-xl shadow-sm overflow-hidden flex flex-col">
        <!-- Toolbar -->
        <div class="p-4 border-b border-outline-variant bg-surface-container-lowest flex flex-col lg:flex-row lg:items-center gap-4 justify-between">
          <div class="relative w-full lg:w-96">
            <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[20px]">search</span>
            <input 
              type="text" 
              placeholder="按姓名、工号或邮箱搜索..." 
              class="w-full pl-10 pr-4 py-2 border border-outline-variant rounded-lg text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary outline-none"
            />
          </div>
          <div class="flex flex-wrap items-center gap-3">
            <select class="bg-surface-container-lowest border border-outline-variant rounded-lg py-2 px-3 text-sm text-on-surface focus:outline-none focus:border-primary cursor-pointer outline-none">
              <option value="">所有部门</option>
              <option value="eng">工程部</option>
            </select>
            <select class="bg-surface-container-lowest border border-outline-variant rounded-lg py-2 px-3 text-sm text-on-surface focus:outline-none focus:border-primary cursor-pointer outline-none">
              <option value="">所有状态</option>
              <option value="active">在职</option>
            </select>
            <button class="px-3 py-2 border border-outline-variant rounded-lg text-sm font-medium hover:bg-surface-container-low transition-colors flex items-center gap-2">
              <span class="material-symbols-outlined text-[18px]">filter_list</span> 更多筛选
            </button>
          </div>
        </div>

        <!-- Table -->
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr class="border-b border-outline-variant bg-surface-container-lowest">
                <th class="py-3 px-4 w-12"><input type="checkbox" class="rounded border-outline-variant text-primary" /></th>
                <th class="py-3 px-4 text-xs font-semibold text-on-surface-variant uppercase">员工</th>
                <th class="py-3 px-4 text-xs font-semibold text-on-surface-variant uppercase">工号</th>
                <th class="py-3 px-4 text-xs font-semibold text-on-surface-variant uppercase">职位与部门</th>
                <th class="py-3 px-4 text-xs font-semibold text-on-surface-variant uppercase">状态</th>
                <th class="py-3 px-4 text-xs font-semibold text-on-surface-variant uppercase">绩效</th>
                <th class="py-3 px-4 text-xs font-semibold text-on-surface-variant uppercase text-right">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-variant">
              
                <tr v-for="emp in EMPLOYEES" :key="emp.id" class="hover:bg-surface-bright transition-colors group">
                  <td class="py-3 px-4"><input type="checkbox" class="rounded border-outline-variant text-primary" /></td>
                  <td class="py-3 px-4">
                    <div class="flex items-center gap-3">
                      <img v-if="emp.avatar" :src="emp.avatar" :alt="emp.name" class="w-8 h-8 rounded-full object-cover bg-surface-container-high" />
   <div v-else class="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center text-sm font-medium text-on-surface-variant">{{ emp.name.substring(0,2).toUpperCase() }}</div>
                      <div>
                        <div class="text-sm font-semibold text-on-surface">{{emp.name}}</div>
                        <div class="text-xs font-mono text-on-surface-variant">{{emp.email}}</div>
                      </div>
                    </div>
                  </td>
                  <td class="py-3 px-4 text-xs font-mono text-on-surface-variant">{{emp.id}}</td>
                  <td class="py-3 px-4">
                    <div class="text-sm font-medium text-on-surface">{{emp.role}}</div>
                    <div class="text-xs text-on-surface-variant mt-0.5">{{emp.dept}}</div>
                  </td>
                  <td class="py-3 px-4">
                    <span v-if="emp.status === 'active'" class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-bold bg-secondary/10 text-secondary border border-secondary/20">在职</span>
                    <span v-if="emp.status === 'probation'" class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-bold bg-tertiary/10 text-tertiary border border-tertiary/20">试用期</span>
                    <span v-if="emp.status === 'offboarding'" class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-bold bg-error/10 text-error border border-error/20">离职中</span>
                  </td>
                  <td class="py-3 px-4">
                    <div class="flex items-center gap-1 text-[14px]">
                      <span v-for="idx in 5" :key="idx" class="material-symbols-outlined text-[14px]" :class="idx <= emp.perf ? 'text-secondary' : 'text-outline-variant'" :style="{ fontVariationSettings: idx <= emp.perf ? '\'FILL\' 1' : '\'FILL\' 0' }">star</span>
                      <span v-if="emp.perf === 0" class="text-xs text-on-surface-variant ml-1">暂无</span>
                    </div>
                  </td>
                  <td class="py-3 px-4 text-right">
                    <div class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button class="w-8 h-8 rounded hover:bg-surface-container-high flex items-center justify-center text-on-surface-variant hover:text-primary transition-colors">
                        <span class="material-symbols-outlined text-[18px]">visibility</span>
                      </button>
                      <button class="w-8 h-8 rounded hover:bg-surface-container-high flex items-center justify-center text-on-surface-variant hover:text-primary transition-colors">
                        <span class="material-symbols-outlined text-[18px]">edit</span>
                      </button>
                    </div>
                  </td>
                </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Pagination -->
        <div class="p-4 border-t border-outline-variant bg-surface-container-lowest flex items-center justify-between text-sm">
          <span class="text-on-surface-variant">显示 1 到 3 条，共 1,248 条</span>
          <div class="flex items-center gap-1">
            <button class="w-8 h-8 rounded flex items-center justify-center text-on-surface-variant hover:bg-surface-container-low transition-colors"><span class="material-symbols-outlined text-[18px]">chevron_left</span></button>
            <button class="w-8 h-8 rounded bg-primary text-white font-medium flex items-center justify-center">1</button>
            <button class="w-8 h-8 rounded hover:bg-surface-container-low text-on-surface font-medium flex items-center justify-center transition-colors">2</button>
            <button class="w-8 h-8 rounded hover:bg-surface-container-low text-on-surface font-medium flex items-center justify-center transition-colors">3</button>
            <span class="w-8 h-8 flex items-center justify-center text-on-surface-variant">...</span>
            <button class="w-8 h-8 rounded flex items-center justify-center text-on-surface-variant hover:bg-surface-container-low transition-colors"><span class="material-symbols-outlined text-[18px]">chevron_right</span></button>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
const EMPLOYEES = [
  { id: 'EMP001', name: '张伟', email: 'zhangwei@talentos.com', role: '前端工程师', dept: '工程部', status: 'active', perf: 4, avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCrxqatEHDCXw88vrI_yjVcbb-S0UQKZYDPRmMJ2L8wJtEy0DYS0i0W4nE1L0U_Ks54MgkryE9ck-_dfxqWl3lHFBEY5lCh1xmnR1TuPSnQvchrafaVeAP8WibX2NHz92gFp_qqqTLrrVRtn_T0BSqFVOrSXUoOgk4-Be9JXUpzeU7aqHTP8-LZ7eeY_yQYWohSQOKQbzxch1Q-aF_ZrcDOImPm6QzaN1mjOAari_cfazlK_Bwy4H01sjsVz9SvVoTqomLOvf5bJdVO' },
  { id: 'EMP002', name: '李娜', email: 'lina@talentos.com', role: '产品经理', dept: '产品部', status: 'probation', perf: 0, avatar: null },
  { id: 'EMP003', name: '王强', email: 'wangqiang@talentos.com', role: '后端工程师', dept: '工程部', status: 'active', perf: 5, avatar: null }
];

</script>
