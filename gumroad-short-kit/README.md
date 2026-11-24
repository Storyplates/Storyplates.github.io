# Phone Tips Shorts Studio

An offline-first creator kit for people making original Android and phone-tip Shorts. It combines a source-linked idea library, one daily script draft, four on-screen beats, relevant tags, a prompt builder, and a short publishing quality pass.

The public project is free to fork and adapt. The included daily workflow can publish new versions of a Gumroad **web app product** after the owner creates that product once and adds their own GitHub secrets. Gumroad's API does not create or upload ordinary products/files; the official Gumroad CLI supports publishing new web-app versions to an existing product.

## First product

The `dist/Phone-Tips-Shorts-Studio.zip` archive is generated from the app files. It has `index.html` at its root, as Gumroad requires for web-app products. The initial daily drop is a source-linked example. Review the content before offering it to buyers.

## Daily release setup

1. Create a Gumroad product in the dashboard as a **Web app** product. Choose your price and store details there.
2. Upload the first build from the generated `dist/` folder in the Gumroad product editor, then make that version live.
3. In the GitHub repository, add Actions secret `GUMROAD_ACCESS_TOKEN` with the Gumroad product-edit permission. Add secret `GEMINI_API_KEY` for the Google AI Studio key.
4. Add repository variable `GUMROAD_PRODUCT_ID`. Use the identifier shown in the Gumroad product edit URL.
5. Enable GitHub Actions. Scheduled runs make one original, source-checked draft from an official Android help page, build the offline app, then publish it as a new version of the existing Gumroad web app.

The action does **not** create a fresh Gumroad listing each day. Gumroad does not provide that through its API. It updates the existing web app product with a new daily issue. A scheduled run fails closed if a key is missing or the source/review checks fail. A manual run defaults to a preview; set `publish` to true only when you want that run to become live.

## Local preview

Open `src/index.html` after placing valid `topics.js` and `daily_drop.js` beside it, or run:

```sh
python scripts/build_product.py
```

Then open `dist/index.html` in a modern browser. The product app itself uses no remote scripts or services. The automated draft generator uses the Gemini Developer API and fetches only the public official help page for that day's topic.

## Important

- No product can be guaranteed to sell. The product needs useful content and an audience; publishing daily versions does not guarantee traffic or sales.
- The daily AI script is a draft. Review device-specific paths, claims, title, tags, and visual rights before using it in a public video.
- Do not put API keys in source files or commit history. Add them only through GitHub Actions secrets.
- The GitHub workflow uploads new versions to an existing Gumroad web app product and promotes the version. Buyers receive the update the next time they open the product.

## License

MIT. Google Android Help links belong to their respective publisher. This project is not affiliated with Google or Gumroad.
