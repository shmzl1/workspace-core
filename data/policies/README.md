# 本地知识文件目录

本目录保存可追溯的虚构演示知识和 Manifest。Loader、Splitter、Embedding 与 ChromaDB 索引代码存在，待本地人工验收；`recruitment/` 中内容不代表真实企业制度。

支持 `.md`、`.txt`、`.pdf`、`.docx`。每份知识应通过同目录 `manifest.json` 提供：

- `source_id`
- `title`
- `document_type`
- `department`
- `job_code`
- `version`
- `effective_from`
- `effective_to`
- `is_active`
- `file_path`

推荐文档类型：`JOB_STANDARD`、`RECRUITMENT_RULES`、`INTERVIEW_STANDARD`、`HR_POLICY`。

不得提交真实敏感企业文件、真实候选人简历、员工薪资文件、本地 Chroma 数据、Embedding 缓存或 API Key。文档变更后重启后端可按稳定 Chunk ID 幂等替换同一来源的旧 Chunk。
