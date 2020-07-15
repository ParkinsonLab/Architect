mkdir -p Project

for file in `ls Split_seqs`; do
	cat TEMPLATE_project.py | sed "s|SEQ_NAME|${file}|g" > Project/${file}.py
done