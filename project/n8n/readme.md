# 列出所有可用分类
python n8n_workflow_main.py --list-categories

# 显示已爬取的分类记录
python n8n_workflow_main.py --show-crawled

# 爬取特定分类（例如"AI"和"Marketing"）
python n8n_workflow_main.py --categories AI Marketing

# 爬取所有分类，但跳过已爬取的
python n8n_workflow_main.py --skip-crawled

# 强制更新特定分类，即使已爬取过
python n8n_workflow_main.py --categories AI --force-update

# 结合使用多个选项
python n8n_workflow_main.py --categories AI Marketing --max-workflows 10 --count 30 --headless



python n8n_file_translate.py --list
# 处理单个子目录
python n8n_file_translate.py --dirs automation

# 处理多个子目录
python n8n_file_translate.py --dirs automation marketing sales