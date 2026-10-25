# Materials Science QA Dataset and Model Evaluation

## 1. DARWIN orientation

DARWIN is a series of open-source language models for natural science, mainly materials science, chemistry, and physics. It is based on the 7 billion parameter LLaMA model. The project has three main parts. DARWIN-SIG generates question and answer pairs from scientific papers. DARWIN-BASE is trained for scientific question answering. DARWIN-MDP builds on DARWIN-BASE and performs materials and device prediction tasks, including classification, regression, and inverse design.

DARWIN uses three main data sources. SciQ provides 13,679 multiple-choice science questions. A collection of around six million scientific papers supplies scientific text, with GPT-4 used to create seed question and answer examples. DARWIN-SIG then generates more question and answer data from this literature. Finally, 16 FAIR scientific datasets provide structured data about material properties, chemical compounds, solar cells, and other scientific tasks. DARWIN-MDP was trained using more than 60,000 instruction examples.

I think the weakest part of the pipeline is automatic QA generation. Incorrect GPT-4 seed answers could be repeated across a much larger dataset, while splitting papers may remove important context. The paper also does not report a detailed audit or error rate, making it difficult to judge whether answers, formulas, and numerical values are fully supported.

## 2. Dataset and audit results

I collected 1,500 recent abstracts from the arXiv `cond-mat.mtrl-sci` category. No duplicate arXiv IDs or abstract texts were found. A local Llama 3.2 model classified the abstracts for materials relevance. Manual review of its uncertain cases resulted in 7 rejections and 1,493 retained abstracts.

Mistral Small generated 240 QA candidates covering material properties, synthesis conditions, performance metrics, and questions intended to be unanswerable. Each answerable pair included an exact supporting passage. Before reviewing the data, I defined error categories for unsupported answers, evidence mismatches, unclear questions, incorrect abstentions, formula problems, and incorrect question types.

I randomly sampled 50 pairs using seed 42. Twenty-seven passed without an identified error. Nine had only an incorrect question category, while 14 had a content, evidence, or abstention problem. The observed pair-level error rate was 46%, with an approximate 95% Wilson interval of 33.0% to 59.6%. The substantive error rate in the sample was 28%. After correcting audited errors and removing unsuitable questions, the final dataset contained 231 pairs. Only the random sample was manually audited, so the final dataset error rate remains unknown.

## 3. Qwen evaluation

I evaluated Qwen2.5-1.5B-Instruct on a free Colab T4 GPU. For each record, the model received the source abstract and question. It was instructed to use only the abstract and respond with `Not stated` when the information was absent. No fine-tuning was performed.

Each response was checked against its abstract and labelled as supported, unsupported, or correctly abstained. Qwen produced 166 supported responses out of 231, or 71.9%. Fifty-five responses were unsupported, or 23.8%, and 10 were correctly abstained, or 4.3%. Common failures included invented numbers, incorrect values, incomplete answers, unnecessary abstentions, and one degenerate response containing repeated symbols.

The evaluation also exposed problems in the references. For 27 of the 46 questions labelled `not_stated`, Qwen produced an answer that was supported by the abstract. This suggests that many of those dataset labels are wrong. I treated the abstract as the main evidence source rather than automatically trusting the generated reference. One reviewer assigned all evaluation labels, so borderline decisions may be subjective.

## 4. Critique and next steps

The dataset has limitations at both the source and QA-generation levels. It contains only recent arXiv abstracts from one category, so it may not represent wider materials-science literature. Abstracts also leave out experimental details and limitations. The generated QA pairs contain incorrect categories, weak evidence links, and unreliable `not_stated` labels. Exact passage matching alone does not prove that the passage answers the question.

With another month, I would compare several generation models using metrics for question type, evidence support, and correct abstention. I would present the results in graphs and ask materials-science researchers to review a sample. If enough high-quality training data were available, I would also fine-tune a model and compare its quality and cost with the other approaches.

One question I now want answered is: **Can a small materials LLM reliably separate information stated in the provided text from information it assumes using general scientific knowledge?**
