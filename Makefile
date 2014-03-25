

#----------------
# Phony targets
#----------------
create_output: 
	@-mkdir Output 2>/dev/null || true

# Export articles from SQLite databases and stem and n-gram them
export_articles: articles process_articles
articles: create_output Output/articles/*.txt Output/articles_control/*.txt
process_articles: Output/articles_stemmed/*.txt Output/articles_stemmed/*.txt Output/bigrams.csv Output/bigrams_control.csv

# Build topic models using the exported articles
model: build_model build_control_model
build_model: Output/topic_model.RData Output/topics.mallet Output/topic-state.gz Output/topic-keys.txt Output/topic-doctopics.txt Output/topic-docs.csv
build_control_model: Output/topic_model_control.RData Output/topics_control.mallet Output/topic_control-state.gz Output/topic_control-keys.txt Output/topic_control-doctopics.txt Output/topic-docs_control.csv

# Generate figures and tables for the topic models
output: plots tables validation
plots: Output/plot_corpus_summary.pdf Output/plot_dendro.pdf Output/plot_topic_model_summary.pdf Output/plot_topic_model_summary_control.pdf
tables: Output/table_corpus_summary.md Output/table_ngo_list.md Output/table_topic_model.md Output/table_topic_model_control.md
validation: Output/plot_validation.pdf Output/validation-articles.txt Output/validation-topic-words.csv 

all: export_articles model output


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


#--------
# Plots
#--------
Output/plot_corpus_summary.pdf: Output/media_data.RData R/plot_corpus_summary.R
	@echo "Plotting corpus summary..."
	cd R; Rscript plot_corpus_summary.R

Output/plot_topic_model_summary.pdf: Output/topic_model.RData R/plot_topic_model.R
	@echo "Plotting topic model summary..."
	cd R; Rscript plot_topic_model.R

Output/plot_topic_model_summary_control.pdf: Output/topic_model_control.RData R/plot_topic_model.R
	@echo "Plotting topic model summary for control group..."
	cd R; Rscript plot_topic_model.R control

Output/plot_dendro.pdf: Output/topic_model.RData R/plot_topic_network.R
	@echo "Plotting topic model dendrogram"
	cd R; Rscript plot_topic_network.R

Output/plot_validation.pdf Output/validation-articles.txt Output/validation-topic-words.csv: Output/topic_model.RData Output/media_data.RData R/manual_topic_validation.R
	@echo "Validating topic model..."
	cd R; Rscript manual_topic_validation.R


#-----------------
# Summary tables
#-----------------
Output/table_corpus_summary.md Output/table_ngo_list.md Output/table_topic_model.md: Output/topic_model.RData Output/media_data.RData R/summary_tables.R
	@echo "Creating summary tables of corpus, NGOs, and model..."
	cd R; Rscript summary_tables.R

Output/table_topic_model_control.md: Output/topic_model.RData R/summary_tables.R
	@echo "Creating summary table of control model..."
	cd R; Rscript summary_tables.R control
