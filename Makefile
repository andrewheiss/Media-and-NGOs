

#--------------
# Compilation
#--------------
articles: create_output Output/articles/*.txt Output/articles_control/*.txt
process_articles: Output/articles_stemmed/*.txt Output/articles_stemmed/*.txt Output/bigrams.csv Output/bigrams_control.csv

build_model: Output/topic_model.RData Output/topics.mallet Output/topic-state.gz Output/topic-keys.txt Output/topic-doctopics.txt Output/topic-docs.csv
build_control_model: Output/topic_model_control.RData Output/topics_control.mallet Output/topic_control-state.gz Output/topic_control-keys.txt Output/topic_control-doctopics.txt Output/topic-docs_control.csv

create_output: 
	@#echo "Creating output folder structure..."
	@-mkdir Output 2>/dev/null || true


#------------------------------
# Export and process articles
#------------------------------
Output/articles/*.txt: prepare_corpus/export_to_mallet.py Corpora/egypt_independent.db Corpora/ahram.db Corpora/dne.db
	@echo "Exporting articles that mention NGOs (this can take a while)..."
	@-mkdir Output/articles 2>/dev/null || true
	python3 prepare_corpus/export_to_mallet.py Corpora/egypt_independent.db egypt_independent Output/articles
	python3 prepare_corpus/export_to_mallet.py Corpora/ahram.db ahram Output/articles
	python3 prepare_corpus/export_to_mallet.py Corpora/dne.db dne Output/articles

Output/articles_control/*.txt: prepare_corpus/export_to_mallet.py Corpora/egypt_independent.db Corpora/ahram.db Corpora/dne.db
	@echo "Exporting control articles..."
	@-mkdir Output/articles_control 2>/dev/null || true
	python3 prepare_corpus/export_to_mallet.py Corpora/egypt_independent.db egypt_independent Output/articles_control --control
	python3 prepare_corpus/export_to_mallet.py Corpora/ahram.db ahram Output/articles_control --control
	python3 prepare_corpus/export_to_mallet.py Corpora/dne.db dne Output/articles_control --control

Output/articles_stemmed/*.txt Output/bigrams.csv: prepare_corpus/process_natural_language.py Output/articles/*.txt
	@echo "Processing NGO articles (this can take a while)..."
	@-mkdir Output/articles_stemmed 2>/dev/null || true
	python2 prepare_corpus/process_natural_language.py Output/articles/ Output/articles_stemmed prepare_corpus/stopwords.txt Output/bigrams.csv

Output/articles_control/stemmed/*.txt Output/bigrams_control.csv: prepare_corpus/process_natural_language.py Output/articles_control/*.txt
	@echo "Processing control articles (this can take a while)..."
	@-mkdir Output/articles_control_stemmed 2>/dev/null || true
	python2 prepare_corpus/process_natural_language.py Output/articles_control/ Output/articles_control_stemmed prepare_corpus/stopwords.txt Output/bigrams_control.csv


#----------
# R stuff
#----------
Output/media_data.RData: R/load_data.R
	@echo "Loading NGO articles into R (this can take a while)..."
	cd R; Rscript load_data.R


#--------------------
# Build topic model
#--------------------
Output/topic_model.RData Output/topics.mallet Output/topic-state.gz Output/topic-keys.txt Output/topic-doctopics.txt Output/topic-docs.csv: R/create_topic_model.R
	@echo "Building topic model (this can take a while)..."
	cd R; Rscript create_topic_model.R

Output/topic_model_control.RData Output/topics_control.mallet Output/topic_control-state.gz Output/topic_control-keys.txt Output/topic_control-doctopics.txt Output/topic-docs_control.csv: R/create_topic_model.R
	@echo "Building control topic model (this can take a while)..."
	cd R; Rscript create_topic_model.R control
