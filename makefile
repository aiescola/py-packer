
deleteOptimized:
	find . -type d -name "*_optimized" -exec rm -rf {} \;

deleteOriginals:
	find . -name "*.jp*g" -exec dirname {} \; | sed 's|\ |\\ |g' | uniq  | grep -v _optimized | xargs rm -rf

