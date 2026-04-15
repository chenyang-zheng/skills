.PHONY: wechat-article-reader clean

wechat-article-reader:
	@echo "Packaging wechat-article-reader..."
	@cd wechat-article-reader && zip -r ../wechat-article-reader.zip . -x "*.DS_Store"
	@echo "Successfully created wechat-article-reader.zip."

clean:
	@echo "Cleaning up..."
	@rm -f *.zip
