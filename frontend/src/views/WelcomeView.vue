<template>
  <div class="text-on-surface bg-surface min-h-screen antialiased selection:bg-primary-container/20 selection:text-on-surface font-sans overflow-x-hidden">


    <!-- Header / Navigation with Glassmorphism -->
    <header class="fixed top-0 left-0 right-0 h-[60px] bg-surface-container-lowest/40 backdrop-blur-xl border-b border-outline-variant/30 z-50 px-6 flex justify-between items-center transition-all duration-300 shadow-sm">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded bg-gradient-to-br from-primary to-primary-container flex items-center justify-center shadow-[0_0_15px_rgba(27,77,255,0.4)]">
          <Cpu class="text-white w-4.5 h-4.5" />
        </div>
        <span class="text-[18px] font-bold text-on-surface tracking-tight">TalentFlow <span class="text-xs font-semibold text-primary px-1.5 py-0.5 rounded bg-primary/10 ml-1">智聘中枢</span></span>
      </div>
      <div class="hidden md:flex gap-8 items-center">
        <a class="text-[12px] font-bold text-on-surface-variant hover:text-primary transition-colors uppercase tracking-wider" href="#features">平台特性</a>
        <a class="text-[12px] font-bold text-on-surface-variant hover:text-primary transition-colors uppercase tracking-wider" href="#security">安全可信</a>
      </div>
      <div>
        <button 
          @click="handleEnterPlatform"
          class="bg-primary text-white text-[12px] font-bold px-4.5 py-2 rounded-lg hover:bg-primary-container transition-all duration-200 flex items-center gap-2 shadow-sm hover:shadow-[0_4px_12px_rgba(27,77,255,0.25)] cursor-pointer active:scale-98"
        >
          进入工作台
          <ArrowRight class="w-4 h-4" />
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="pt-[60px]">
      <!-- Hero Section with Interactive Canvas -->
      <section class="relative py-24 md:py-32 flex items-center justify-center overflow-hidden bg-surface-container-lowest">
        <div class="absolute inset-0 hero-pattern opacity-35"></div>
        
        <!-- Interactive Canvas Background -->
        <canvas ref="canvasRef" class="absolute inset-0 w-full h-full pointer-events-none" />
        
        <!-- Neon Floating blur balls with orbiting motion -->
        <div class="absolute top-1/4 left-10 w-80 h-80 bg-primary-container/10 rounded-full mix-blend-multiply filter blur-[100px] animate-orbit-slow-1"></div>
        <div class="absolute bottom-1/4 right-10 w-96 h-96 bg-secondary-container/15 rounded-full mix-blend-multiply filter blur-[120px] animate-orbit-slow-2"></div>
        
        <div class="container w-full mx-auto px-6 max-w-6xl relative z-10 grid grid-cols-1 md:grid-cols-12 gap-12 items-center">
          <div class="md:col-span-7 w-full flex flex-col items-start text-left max-w-2xl">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-container border border-outline-variant/40 mb-6">
              <span class="w-2 h-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(27,77,255,0.6)]"></span>
              <span class="text-[11px] font-bold text-outline tracking-wider uppercase">企业级可解释 HR Agent 协同系统</span>
            </div>
            
            <h1 class="text-[36px] md:text-[46px] font-extrabold text-on-surface mb-6 leading-tight tracking-tight">
              大模型驱动的<br />
              <span class="bg-clip-text text-transparent bg-gradient-to-r from-primary via-primary-container to-tertiary font-black">企业级智能人才管理</span><br />
              与合规审计平台
            </h1>
            
            <p class="text-[14px] text-on-surface-variant mb-8 leading-relaxed w-full">
              构建面向招聘决策、员工服务、考勤薪资预审与权限审计的企业智能体枢纽。为您提供严密、透明且安全的人力资源管理效率引擎，让 HR 决策与财务审核尽在掌控。
            </p>

            <!-- Quick Access Role Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">
              <!-- HR Card -->
              <button 
                @click="handleNavigate('hr')"
                class="flex items-center gap-4 p-4.5 bg-surface-container-lowest/80 backdrop-blur-md border border-outline-variant/40 rounded-xl hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 cursor-pointer text-left group active:scale-98"
              >
                <div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary group-hover:scale-105 transition-transform duration-300">
                  <Rocket class="w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-sm font-bold text-on-surface flex items-center gap-1">
                    HR 管理门户
                    <ArrowRight class="w-3.5 h-3.5 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-350" />
                  </h3>
                  <p class="text-xs text-on-surface-variant mt-1">智能简历评估与协同排期</p>
                </div>
              </button>

              <!-- Employee Card -->
              <button 
                @click="handleNavigate('employee')"
                class="flex items-center gap-4 p-4.5 bg-surface-container-lowest/80 backdrop-blur-md border border-outline-variant/40 rounded-xl hover:border-tertiary/40 hover:shadow-lg hover:shadow-tertiary/5 transition-all duration-300 cursor-pointer text-left group active:scale-98"
              >
                <div class="w-12 h-12 rounded-lg bg-tertiary/10 flex items-center justify-center text-tertiary group-hover:scale-105 transition-transform duration-300">
                  <Cpu class="w-6 h-6" />
                </div>
                <div>
                  <h3 class="text-sm font-bold text-on-surface flex items-center gap-1">
                    员工智能助手
                    <ArrowRight class="w-3.5 h-3.5 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-350" />
                  </h3>
                  <p class="text-xs text-on-surface-variant mt-1">假勤薪资自助与政策问答</p>
                </div>
              </button>
            </div>
          </div>
          
          <!-- Animated Agent Code Terminal -->
          <div class="md:col-span-5 w-full h-[300px] md:h-[360px] rounded-2xl overflow-hidden shadow-2xl border border-outline-variant/40 bg-surface-container-lowest flex flex-col group relative">
            <div class="h-9 bg-surface-container border-b border-outline-variant/30 flex items-center px-4 gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-red-400"></span>
              <span class="w-2.5 h-2.5 rounded-full bg-yellow-400"></span>
              <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
              <span class="text-xs text-outline font-mono ml-2">TalentFlow-Agent-Hub.log</span>
            </div>
            
            <div class="flex-1 bg-[#090d16]/95 p-5 font-mono text-[11px] text-primary-fixed-dim overflow-y-auto custom-scrollbar flex flex-col justify-end leading-relaxed select-text border-t border-white/5 shadow-inner">
              <div class="space-y-1.5">
                <p v-for="(line, index) in visibleLines" :key="index" class="opacity-80">
                  <span v-if="line.startsWith('> ')" class="text-primary-container font-bold mr-1.5">&gt;</span>
                  <span>{{ line.startsWith('> ') ? line.substring(2) : line }}</span>
                </p>
                
                <p v-if="currentText" class="flex items-center">
                  <span v-if="currentText.startsWith('> ')" class="text-primary-container font-bold mr-1.5">&gt;</span>
                  <span>{{ currentText.startsWith('> ') ? currentText.substring(2) : currentText }}</span>
                  <span class="w-1.5 h-3.5 bg-primary-container animate-pulse inline-block ml-0.5" />
                </p>
                
                <p v-if="!currentText && currentLineIndex < TERMINAL_LINES.length" class="flex items-center">
                  <span class="w-1.5 h-3.5 bg-primary-container animate-pulse inline-block" />
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Features Bento Grid with Hover Border Glow -->
      <section class="py-24 bg-surface border-t border-outline-variant/30" id="features">
        <div class="container w-full mx-auto px-6 max-w-6xl">
          <div class="text-center mb-16">
            <h2 class="text-[26px] font-extrabold text-on-surface mb-4 tracking-tight">平台核心能力</h2>
            <p class="text-[14px] text-on-surface-variant w-full max-w-2xl mx-auto leading-relaxed">
              为企业提供从招聘管理到财务审计的闭环人机协同系统，构建安全隔离的内部 Agent 运营管线。
            </p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
            <!-- Bento Box 1: Recruitment (Span 8) -->
            <div class="md:col-span-8 w-full bg-surface-container-lowest rounded-2xl border border-outline-variant/40 p-8 shadow-sm flex flex-col md:flex-row gap-8 items-center hover:shadow-[0_12px_30px_rgba(27,77,255,0.06)] hover:border-primary/20 hover:-translate-y-1 transition-all duration-300 group">
              <div class="flex-1">
                <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary border border-primary/20 mb-6 shadow-sm">
                  <Library class="w-5 h-5" />
                </div>
                <h3 class="text-[18px] font-bold text-on-surface mb-3">多维招聘决策 Agent</h3>
                <p class="text-[13px] text-on-surface-variant mb-5 leading-relaxed">
                  多智能体协同评估，从简历自动提取、全流程匹配评分到面试自动排期。平台提供结构化的评分指标与依据，确保筛选流程有据可查、透明可信。
                </p>
                <ul class="space-y-2">
                  <li class="flex items-center gap-2 text-[12px] font-semibold text-on-surface-variant">
                    <CheckCircle2 class="text-primary w-4 h-4" /> 简历结构化深度打分评估
                  </li>
                  <li class="flex items-center gap-2 text-[12px] font-semibold text-on-surface-variant">
                    <CheckCircle2 class="text-primary w-4 h-4" /> 多方日程匹配与智能面试排期
                  </li>
                </ul>
              </div>
              
              <!-- Mini-Visual Mockup inside Bento Card -->
              <div class="flex-1 w-full h-44 bg-surface rounded-xl border border-outline-variant/30 p-4 relative overflow-hidden shadow-inner flex flex-col justify-between">
                <div class="flex items-center justify-between border-b border-outline-variant/20 pb-2">
                  <span class="text-xs font-bold text-on-surface">候选人智能匹配度评估</span>
                  <span class="text-xs font-extrabold text-primary bg-primary/10 px-2 py-0.5 rounded">92分</span>
                </div>
                <div class="space-y-2 py-2 flex-1 flex flex-col justify-center">
                  <div class="flex justify-between text-[10px]">
                    <span class="text-outline">技术栈契合度</span>
                    <span class="font-bold">95%</span>
                  </div>
                  <div class="w-full h-1.5 bg-surface-container rounded-full overflow-hidden">
                    <div class="h-full bg-primary w-[95%] rounded-full"></div>
                  </div>
                  <div class="flex justify-between text-[10px]">
                    <span class="text-outline">行业经验匹配</span>
                    <span class="font-bold">88%</span>
                  </div>
                  <div class="w-full h-1.5 bg-surface-container rounded-full overflow-hidden">
                    <div class="h-full bg-primary w-[88%] rounded-full"></div>
                  </div>
                </div>
                <div class="text-[9px] text-outline text-right italic">
                  * 评估结果不直接做录用/淘汰决策，仅供 HR 参考。
                </div>
              </div>
            </div>
            
            <!-- Bento Box 2: Leave & Assistant (Span 4) -->
            <div class="md:col-span-4 w-full bg-surface-container-lowest rounded-2xl border border-outline-variant/40 p-8 shadow-sm flex flex-col hover:shadow-[0_12px_30px_rgba(27,77,255,0.06)] hover:border-primary/20 hover:-translate-y-1 transition-all duration-300 group">
              <div class="w-12 h-12 bg-tertiary/10 rounded-xl flex items-center justify-center text-tertiary border border-tertiary/20 mb-6 shadow-sm">
                <Lightbulb class="w-5 h-5" />
              </div>
              <h3 class="text-[18px] font-bold text-on-surface mb-3">员工智能假勤小秘书</h3>
              <p class="text-[13px] text-on-surface-variant mb-5 flex-grow leading-relaxed">
                微信小程序多端集成，支持对话式假期额度查询、加班签到核准。内置政企合规知识库 RAG，秒级提供精准的公司制度和政策问答。
              </p>
              <span class="text-[12px] font-bold text-primary hover:text-primary-container flex items-center gap-1 mt-auto cursor-pointer">
                快速了解小程序 &rarr;
              </span>
            </div>

            <!-- Bento Box 3: Salary Pre-audit (Span 12 Full Width dark card) -->
            <div class="md:col-span-12 w-full bg-[#090d16] rounded-2xl border border-white/5 p-8 shadow-md text-white overflow-hidden relative">
              <div class="absolute inset-0 opacity-5 bg-[radial-gradient(#ffffff_1px,transparent_1px)]" style="background-size: 20px 20px;"></div>
              
              <div class="relative z-10 flex flex-col md:flex-row gap-8 items-center">
                <div class="flex-1">
                  <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/20 mb-6">
                    <span class="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                    <span class="text-[11px] font-bold text-white/80 tracking-wider">合规与薪资预审控制舱</span>
                  </div>
                  <h3 class="text-[20px] font-extrabold text-white mb-3 tracking-tight">智能考勤薪资交叉审计</h3>
                  <p class="text-[13px] text-white/70 mb-6 leading-relaxed">
                    在发放考勤与计算薪资前，由后台合规算法对考勤打卡状态、请假历史明细与薪资系数进行自动映射核查。预警漏签和系数异常，杜绝人为差错与财务漏损风险，实现发放前的合规预审计。
                  </p>
                  <div class="flex flex-wrap gap-4 text-xs font-semibold text-white/80">
                    <span class="flex items-center gap-1.5 bg-white/5 px-3 py-1.5 rounded-lg border border-white/10">
                      <span class="w-1.5 h-1.5 rounded-full bg-[#10b981]"></span>
                      打卡漏签智能诊断
                    </span>
                    <span class="flex items-center gap-1.5 bg-white/5 px-3 py-1.5 rounded-lg border border-white/10">
                      <span class="w-1.5 h-1.5 rounded-full bg-[#10b981]"></span>
                      薪资发放前差错审计
                    </span>
                  </div>
                </div>
                
                <!-- Terminal / Visual Grid representing data checking -->
                <div class="flex-1 w-full bg-white/5 border border-white/10 rounded-xl p-5 flex flex-col gap-3 font-mono text-[10px] text-white/70">
                  <div class="border-b border-white/10 pb-2 flex justify-between text-white font-bold text-xs">
                    <span>系统薪资审计警报</span>
                    <span class="text-red-400">检测到1项异常</span>
                  </div>
                  <div class="space-y-1.5">
                    <p class="text-green-400">[PASS] 基础薪资范围验证匹配。</p>
                    <p class="text-green-400">[PASS] 部门管理岗位加权系数校验通过。</p>
                    <p class="text-red-400">[WARN] 员工李明：考勤表中包含 3 天无假条缺勤，但薪资未扣减。</p>
                    <p class="text-yellow-400">[ACTION] 建议：发起考勤异常复核流，核实后再准予发放。</p>
                  </div>
                  <div class="text-[9px] text-white/40 border-t border-white/5 pt-2 italic">
                    * 薪资系统仅做预审分析警报，实际金额修改与发放必须经 HR 人工终审确认。
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Enterprise Trust & Security Section -->
      <section class="py-24 bg-surface-container-lowest border-t border-outline-variant/30" id="security">
        <div class="container w-full mx-auto px-6 max-w-6xl">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <div>
              <h2 class="text-[26px] font-extrabold text-on-surface mb-6 tracking-tight">可信运营与企业级数据合规</h2>
              <p class="text-[14px] text-on-surface-variant mb-8 leading-relaxed">
                HR 与薪资资产关系重大。我们通过本地化沙箱限制、细粒度脱敏以及可解释的推理审计，让大模型完全在安全可控范围内为企业创造效率价值。
              </p>
              
              <div class="space-y-6">
                <!-- Point 1 -->
                <div class="flex gap-4">
                  <div class="w-10 h-10 rounded-full bg-surface border border-outline-variant/40 flex items-center justify-center text-on-surface shrink-0 shadow-sm">
                    <Shield class="w-4.5 h-4.5" />
                  </div>
                  <div>
                    <h4 class="text-sm font-semibold text-on-surface mb-1">私有化本地网络架构</h4>
                    <p class="text-xs text-on-surface-variant leading-relaxed">
                      支持部署于企业 VPC 内部局域网，在完全不访问公网的沙箱化容器内运行推理，确保核心员工隐私及工资单资产不离企业。
                    </p>
                  </div>
                </div>
                
                <!-- Point 2 -->
                <div class="flex gap-4">
                  <div class="w-10 h-10 rounded-full bg-surface border border-outline-variant/40 flex items-center justify-center text-on-surface shrink-0 shadow-sm">
                    <History class="w-4.5 h-4.5" />
                  </div>
                  <div>
                    <h4 class="text-sm font-semibold text-on-surface mb-1">操作全链路留痕审计</h4>
                    <p class="text-xs text-on-surface-variant leading-relaxed">
                      所有关于简历修改、考勤审查批复与薪资数据存取的智能分析操作，均写入系统的审计流水账。完全符合严苛的审计合规标准。
                    </p>
                  </div>
                </div>
                
                <!-- Point 3 -->
                <div class="flex gap-4">
                  <div class="w-10 h-10 rounded-full bg-surface border border-outline-variant/40 flex items-center justify-center text-on-surface shrink-0 shadow-sm">
                    <ShieldCheck class="w-4.5 h-4.5" />
                  </div>
                  <div>
                    <h4 class="text-sm font-semibold text-on-surface mb-1">精细化权限访问限制</h4>
                    <p class="text-xs text-on-surface-variant leading-relaxed">
                      智能助手严格遵循既有 HR 角色权限边界，严禁绕过 API 隔离鉴权，对敏感字段自动实施前端脱敏与后端拦截限制。
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="w-full h-full bg-surface rounded-2xl border border-outline-variant/40 p-8 flex flex-col items-center justify-start text-center shadow-inner relative overflow-hidden group">
              <!-- Animated Background Elements -->
              <div class="absolute -top-12 -right-12 w-32 h-32 bg-primary/10 rounded-full filter blur-2xl group-hover:bg-primary/20 transition-all duration-700"></div>
              <div class="absolute -bottom-12 -left-12 w-32 h-32 bg-tertiary/10 rounded-full filter blur-2xl group-hover:bg-tertiary/20 transition-all duration-700"></div>
              
              <div class="relative w-16 h-16 flex items-center justify-center mb-6 mt-2">
                <div class="absolute inset-0 bg-primary/10 rounded-full animate-ping" style="animation-duration: 3s;"></div>
                <div class="absolute inset-2 bg-primary/20 rounded-full animate-pulse"></div>
                <ShieldAlert class="w-8 h-8 text-primary relative z-10" />
              </div>
              
              <h3 class="text-lg font-bold text-on-surface mb-3">安全红线保障</h3>
              <p class="text-xs text-on-surface-variant w-full leading-relaxed mb-8">
                遵循最高数据处理合规标准，用完即弃的会话上下文缓存策略，不积累、不挪用员工敏感数据。
              </p>
              
              <!-- Mock Security Status Logs -->
              <div class="w-full flex-1 bg-surface-container border border-outline-variant/30 rounded-xl p-4 flex flex-col gap-3 text-left font-mono text-[10px] overflow-hidden relative shadow-inner">
                <div class="flex items-center justify-between text-xs font-bold text-on-surface border-b border-outline-variant/30 pb-2 mb-1">
                  <span>SYSTEM_AUDIT</span>
                  <span class="text-primary flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span> ACTIVE</span>
                </div>
                
                <div class="flex items-start gap-2">
                  <CheckCircle2 class="w-3.5 h-3.5 text-green-500 mt-0.5 shrink-0" />
                  <div>
                    <div class="text-on-surface font-semibold">数据加密隔离</div>
                    <div class="text-on-surface-variant/70 text-[9px] mt-0.5">VPC 端到端加密验证通过</div>
                  </div>
                </div>
                
                <div class="flex items-start gap-2">
                  <CheckCircle2 class="w-3.5 h-3.5 text-green-500 mt-0.5 shrink-0" />
                  <div>
                    <div class="text-on-surface font-semibold">会话沙箱销毁</div>
                    <div class="text-on-surface-variant/70 text-[9px] mt-0.5">上下文缓存在 30s 内已释放</div>
                  </div>
                </div>
                
                <div class="flex items-start gap-2">
                  <CheckCircle2 class="w-3.5 h-3.5 text-green-500 mt-0.5 shrink-0" />
                  <div>
                    <div class="text-on-surface font-semibold">权限溯源拦截</div>
                    <div class="text-on-surface-variant/70 text-[9px] mt-0.5">零越权，敏感字段实时脱敏</div>
                  </div>
                </div>

                <!-- Gradient fade out at bottom if it gets too long -->
                <div class="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-surface-container to-transparent pointer-events-none"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA Section with Glowing Flow -->
      <section class="py-24 bg-[#090d16] text-center px-6 relative overflow-hidden border-t border-white/5">
        <div class="absolute inset-0 opacity-5 bg-[radial-gradient(#ffffff_1px,transparent_1px)]" style="background-size: 24px 24px;"></div>
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary/10 rounded-full blur-[100px] pointer-events-none"></div>
        
        <h2 class="text-[28px] font-extrabold text-white mb-6 tracking-tight relative z-10">立即开启可信企业人才中枢</h2>
        <p class="text-[14px] text-white/70 mb-10 max-w-2xl mx-auto leading-relaxed relative z-10">
          通过多阶段智能体，重塑招聘评筛效率与内部行政协同效率。
        </p>
        <div class="flex justify-center relative z-10">
          <button 
            @click="handleEnterPlatform"
            class="bg-primary text-white text-[12px] font-bold px-8 py-3.5 rounded-lg hover:bg-primary-container transition-all duration-200 shadow-[0_4px_16px_rgba(27,77,255,0.4)] hover:-translate-y-0.5 active:translate-y-0 cursor-pointer active:scale-98"
          >
            立即登录工作台
          </button>
        </div>
      </section>
    </main>

    <footer class="bg-surface-container border-t border-outline-variant/30 py-8 px-6 text-center text-outline text-xs">
      <p>© 2026 TalentFlow Enterprise HR Agent System. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../features/auth/authStore';
import { 
  Cpu, ArrowRight, Rocket, Library, CheckCircle2, 
  Lightbulb, Shield, History, ShieldCheck, ShieldAlert 
} from 'lucide-vue-next';

const router = useRouter();
const auth = useAuthStore();

// Navigation logic based on login state
function handleEnterPlatform() {
  if (auth.isAuthenticated.value) {
    if (auth.hasPermission('recruitment.read')) {
      router.push('/hr/dashboard');
    } else {
      router.push('/employee/dashboard');
    }
  } else {
    router.push('/login');
  }
}

function handleNavigate(role: 'hr' | 'employee') {
  if (auth.isAuthenticated.value) {
    if (role === 'hr') {
      if (auth.hasPermission('recruitment.read')) {
        router.push('/hr/dashboard');
      } else {
        router.push('/employee/dashboard');
      }
    } else {
      router.push('/employee/dashboard');
    }
  } else {
    router.push('/login');
  }
}

// 1. Particle Canvas Setup
const canvasRef = ref<HTMLCanvasElement | null>(null);
let animationFrameId: number;

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  baseVx: number;
  baseVy: number;
  radius: number;
  color: string;
}

function initParticleCanvas() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  let width = (canvas.width = canvas.offsetWidth || window.innerWidth);
  let height = (canvas.height = canvas.offsetHeight || window.innerHeight);

  const particles: Particle[] = [];
  
  const initParticles = () => {
    particles.length = 0;
    const particleCount = Math.min(100, Math.floor((width * height) / 12000));
    for (let i = 0; i < particleCount; i++) {
      const baseSpeed = Math.random() * 0.4 + 0.2;
      const angle = Math.random() * Math.PI * 2;
      const isBlue = Math.random() > 0.45;
      
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: Math.cos(angle) * baseSpeed,
        vy: Math.sin(angle) * baseSpeed,
        baseVx: Math.cos(angle) * baseSpeed,
        baseVy: Math.sin(angle) * baseSpeed,
        radius: Math.random() * 2.2 + 1.2,
        color: isBlue ? 'rgba(0, 55, 208, 0.35)' : 'rgba(99, 102, 241, 0.35)',
      });
    }
  };

  initParticles();

  const mouse = { x: -1000, y: -1000 };

  const handleMouseMove = (e: MouseEvent) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  };

  const handleMouseLeave = () => {
    mouse.x = -1000;
    mouse.y = -1000;
  };

  window.addEventListener('mousemove', handleMouseMove);
  canvas.addEventListener('mouseleave', handleMouseLeave);

  const handleResize = () => {
    if (!canvas) return;
    width = canvas.width = canvas.offsetWidth || window.innerWidth;
    height = canvas.height = canvas.offsetHeight || window.innerHeight;
    if (particles.length === 0 && width > 0) {
      initParticles();
    }
  };
  window.addEventListener('resize', handleResize);

  const draw = () => {
    ctx.clearRect(0, 0, width, height);
    
    for (let i = 0; i < particles.length; i++) {
      const p1 = particles[i];
      p1.x += p1.vx;
      p1.y += p1.vy;
      
      if (p1.x < 0 || p1.x > width) p1.vx *= -1;
      if (p1.y < 0 || p1.y > height) p1.vy *= -1;

      if (mouse.x > -1000) {
        const dx = p1.x - mouse.x;
        const dy = p1.y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 160) {
          const force = (160 - dist) / 160;
          p1.vx += (dx / dist) * force * 0.8;
          p1.vy += (dy / dist) * force * 0.8;
        }
      }

      p1.vx = p1.vx * 0.94 + p1.baseVx * 0.06;
      p1.vy = p1.vy * 0.94 + p1.baseVy * 0.06;

      const speed = Math.sqrt(p1.vx * p1.vx + p1.vy * p1.vy);
      if (speed > 4) {
        p1.vx = (p1.vx / speed) * 4;
        p1.vy = (p1.vy / speed) * 4;
      }

      ctx.beginPath();
      ctx.arc(p1.x, p1.y, p1.radius, 0, Math.PI * 2);
      ctx.fillStyle = p1.color;
      ctx.fill();

      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 140) {
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          const alpha = 0.2 * (1 - dist / 140);
          ctx.strokeStyle = p1.color === p2.color ? p1.color.replace('0.35', alpha.toFixed(3)) : `rgba(165, 180, 252, ${alpha.toFixed(3)})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }

    animationFrameId = requestAnimationFrame(draw);
  };

  draw();

  return () => {
    cancelAnimationFrame(animationFrameId);
    window.removeEventListener('mousemove', handleMouseMove);
    canvas.removeEventListener('mouseleave', handleMouseLeave);
    window.removeEventListener('resize', handleResize);
  };
}

// 2. Typing Terminal Setup
const TERMINAL_LINES = [
  '> Initializing TalentFlow HR agent cluster... [OK]',
  '> Connecting to local vector index database...',
  '> Vector index ready: 34 core corporate policy documents loaded.',
  '> Fetching candidate profiles for the pipeline...',
  '> Parsing resume: "张伟_资深前端开发.pdf" -> Structuring profile...',
  '> [Agent] Generated evaluation score: 92/100.',
  '> Finding mutual availability for interviewer panel...',
  '> Automatic interview schedules proposed. [Success]',
  '> [Audit] Verifying employee salary access boundaries...',
  '> [Audit] OK: Strictly verified and columns masked.',
  '> Pre-auditing payroll calculation for July 2026...',
  '> Auto-audited payroll difference index: 0.001. [OK]',
  '> Pre-audit draft report created: "TalentFlow_July_PreAudit_Draft.xlsx".',
  '> System standby. Ready for HR manual decision check.'
];

const visibleLines = ref<string[]>([]);
const currentLineIndex = ref(0);
const charIndex = ref(0);
const currentText = ref('');
let terminalTimer: number | undefined;

function runTypingEffect() {
  if (currentLineIndex.value >= TERMINAL_LINES.length) {
    terminalTimer = window.setTimeout(() => {
      visibleLines.value = [];
      currentLineIndex.value = 0;
      charIndex.value = 0;
      currentText.value = '';
      runTypingEffect();
    }, 4000);
    return;
  }

  const currentLine = TERMINAL_LINES[currentLineIndex.value];
  if (charIndex.value < currentLine.length) {
    terminalTimer = window.setTimeout(() => {
      currentText.value += currentLine[charIndex.value];
      charIndex.value++;
      runTypingEffect();
    }, 20 + Math.random() * 15);
  } else {
    terminalTimer = window.setTimeout(() => {
      visibleLines.value.push(currentLine);
      currentText.value = '';
      charIndex.value = 0;
      currentLineIndex.value++;
      runTypingEffect();
    }, 850);
  }
}

// Global Lifecycle
let destroyCanvas: (() => void) | undefined;

onMounted(() => {
  destroyCanvas = initParticleCanvas();
  runTypingEffect();
});

onUnmounted(() => {
  if (destroyCanvas) destroyCanvas();
  if (terminalTimer) window.clearTimeout(terminalTimer);
});
</script>

<style scoped>
.hero-pattern {
  background-image: radial-gradient(var(--color-outline-variant) 1px, transparent 1px);
  background-size: 24px 24px;
}
@keyframes orbit {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(40px, -60px) scale(1.15); }
  66% { transform: translate(-30px, 30px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
.animate-orbit-slow-1 {
  animation: orbit 15s ease-in-out infinite;
}
.animate-orbit-slow-2 {
  animation: orbit 20s ease-in-out infinite;
  animation-delay: 3s;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(27, 77, 255, 0.2);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(27, 77, 255, 0.4);
}
</style>

