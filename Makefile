
# export articles from corpus
# stem, etc. articles
# build topic model
# load data
# make graphs and tables

#--------------
# Compilation
#--------------
articles: create_output Output/articles/*.txt

create_output: 
	@echo "Creating output folder structure..."
	@-mkdir Output 2>/dev/null || true
	@-mkdir Output/articles 2>/dev/null || true
	@-mkdir Output/articles_control 2>/dev/null || true


#------------------------------
# Export and process articles
#------------------------------
Output/articles/*.txt: prepare_corpus/export_to_mallet.py Corpora/egypt_independent.db Corpora/ahram.db Corpora/dne.db
	@echo "Exporting articles that mention NGOs (this can take a while)..."
	python3 prepare_corpus/export_to_mallet.py Corpora/egypt_independent.db egypt_independent Output/articles
	python3 prepare_corpus/export_to_mallet.py Corpora/ahram.db ahram Output/articles
	python3 prepare_corpus/export_to_mallet.py Corpora/dne.db dne Output/articles

	@echo "Exporting control articles..."
	python3 prepare_corpus/export_to_mallet.py Corpora/egypt_independent.db egypt_independent Output/articles_control --control
	python3 prepare_corpus/export_to_mallet.py Corpora/ahram.db ahram Output/articles_control --control
	python3 prepare_corpus/export_to_mallet.py Corpora/dne.db dne Output/articles_control --control


#---------
# Tables
#---------


#--------
# Plots
#--------
