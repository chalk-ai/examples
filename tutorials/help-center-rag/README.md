# Answer support questions with RAG in Chalk SQL

A support assistant answers customer questions from a fictional lender's help-center
articles. The tutorial runs in a Chalk notebook: it embeds the articles, retrieves the
passages closest to a question, writes an answer with citations, and evaluates the
answers with a Chalk Evaluation.

## Files

| File | Contents |
| --- | --- |
| `data/articles.json` | 40 help-center articles in three topics (Payments, Fees, Account access). Each has an `id`, `topic`, `title`, and a `body` of three paragraphs separated by blank lines. |
| `data/questions.json` | 14 customer questions, each with the ids of the articles that answer it (`expected`). |

The notebook downloads both files from this repository, so you don't need to clone it.
