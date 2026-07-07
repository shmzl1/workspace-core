<template>
  <section class="agentbar">
    <div class="agentbar__quick">
      <button
        v-for="command in currentCommands"
        :key="command"
        type="button"
        class="whitespace-nowrap"
        @click="fillCommand(command)"
      >
        {{ command }}
      </button>
    </div>

    <form class="agentbar__form" @submit.prevent="submitCommand">
      <span class="agentbar__spark"></span>
      <input
        v-model="commandText"
        :placeholder="role === 'hr' ? '让 TalentFlow AI 筛选候选人、安排面试或生成报表...' : '问问 TalentFlow AI 关于你的假期、薪资或考勤...'"
      />
      <button class="agentbar__send" aria-label="发送指令" type="submit">
        <span></span>
      </button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Role } from '../types';

const props = defineProps<{
  role: Role;
}>();

const emit = defineEmits<{
  submitCommand: [command: string];
}>();

const commandText = ref('');

const currentCommands = computed(() => {
  if (props.role === 'hr') {
    return [
      '筛选 Java 后端候选人',
      '安排本周技术面',
      '生成招聘周报'
    ];
  } else {
    return [
      '查询我的年假余额',
      '查看我上个月的工资单',
      '帮我请假 2 天'
    ];
  }
});

function fillCommand(command: string) {
  commandText.value = command;
}

function submitCommand() {
  const command = commandText.value.trim();
  if (!command) {
    return;
  }
  emit('submitCommand', command);
  commandText.value = '';
}
</script>

<style scoped lang="scss">
.agentbar {
  position: fixed;
  right: 34px;
  bottom: 20px;
  left: calc(var(--sidebar-width) + 34px);
  z-index: 25;
  display: grid;
  gap: 10px;
}

.agentbar__quick {
  display: flex;
  gap: 9px;
  overflow-x: auto;
  scrollbar-width: none; /* Hide scrollbar for clean design */
  &::-webkit-scrollbar {
    display: none;
  }
}

.agentbar__quick button {
  flex: 0 0 auto;
  padding: 8px 12px;
  border: 1px solid var(--color-line);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  color: var(--color-muted);
  font-size: 13px;
  white-space: nowrap; /* Prevent horizontal overlap and wrapping */
}

.agentbar__form {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 64px;
  padding: 10px 12px 10px 18px;
  border: 1px solid var(--color-line-strong);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 48px rgba(19, 32, 62, 0.14);
  backdrop-filter: blur(18px);
}

.agentbar__spark {
  width: 22px;
  height: 22px;
  border-radius: 7px;
  background:
    linear-gradient(90deg, transparent 43%, #fff 43%, #fff 57%, transparent 57%),
    linear-gradient(0deg, transparent 43%, #fff 43%, #fff 57%, transparent 57%),
    var(--color-primary);
  box-shadow: 0 0 20px rgba(36, 85, 245, 0.35);
}

.agentbar__form input {
  flex: 1;
  min-width: 0;
  border: 0;
  outline: 0;
  color: var(--color-text);
  font-size: 15px;
}

.agentbar__send {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 50%;
  background: var(--color-primary);
  box-shadow: var(--shadow-soft);
}

.agentbar__send span {
  width: 13px;
  height: 13px;
  border-top: 3px solid #fff;
  border-right: 3px solid #fff;
  transform: rotate(45deg);
}

@media (max-width: 980px) {
  .agentbar {
    right: 18px;
    left: 18px;
  }
}
</style>
