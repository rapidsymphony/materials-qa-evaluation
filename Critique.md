## Critique

The dataset has limitations at both the source-document and QA-generation levels. It contains only recent arXiv abstracts from cond-mat.mtrl-sci, so it may not represent the wider materials-science literature. Abstracts are also short and often leave out important experimental details and limitations.

The largest problem was the `not_stated` questions. During evaluation, 27 of the 46 questions labelled `not_stated` received answers that were supported by their abstracts. This suggests that many of these labels are wrong. Some questions were also placed in the wrong category, and exact passage matching did not always mean that the passage supported the answer. Only 50 pairs were manually audited, so the error rate of the final dataset is unknown.

With another month, I would compare several models using metrics for question type, evidence support, and correct not_stated labels. I would present the results in graphs and ask materials-science researchers to review a sample. If enough high-quality training data were available, I would also fine-tune a model and compare its quality and cost with the other approaches.

One question I now want answered is:
Can a small materials LLM reliably separate information stated in the provided text from information it assumes using general scientific knowledge?
