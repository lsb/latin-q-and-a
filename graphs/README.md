# The graphs

Each graph has a script. The script writes a PNG file and a TeX file from the
same numbers. Run the script again to make the two files again.

The text below follows ASD-STE100 (Simplified Technical English): approved
words, active voice, short sentences, and one topic sentence for each
paragraph.

---

## speed-accuracy

This graph shows the accuracy of each model and the time cost of each model.
Each model has two marks. The solid mark shows pass@1. The open mark shows
pass@3. The line between the two marks shows the increase that three tries
give. The horizontal axis shows the mean time for one answer, on a logarithmic
scale.

A solid line connects the models of one family, from small to large. A broken
line connects the instruct build and the think build of one model. The think
build is more accurate, but it is much slower.

## latency-spread

This graph shows the full range of the answer times for the large models. It
shows only the models that have more than 9 billion parameters. Each model has
one shape. The width of the shape shows how many answers have that time. The
thick bar shows the middle half of the times. The white line shows the median,
and the diamond shows the mean.

For some models the mean and the median are not the same. These models have two
groups of answer times, with a large space between the groups. A box plot
cannot show this condition, but this graph can show it.

## consistency

This graph shows if the three answers to one question agree with each other.
Each question gives one of five results. The black line is the pass@3 limit. To
the left of the line, the model gives a correct answer one time or more. To the
right of the line, the model does not give a correct answer.

The colors to the right show the wrong answers. A dark color shows that the
model gives the same wrong answer three times. A pale color shows that the
model gives three different wrong answers. Two answers are the same if the two
answers have the same meaning. Different letters do not make two answers
different.

## provenance-split

This graph compares two types of question. 70 questions come from a Latin text.
69 questions are about Roman life, and have a citation but no text. Each model
has two marks and a line between the two marks. The number at the end of the
line shows the difference in points.

The weak models show almost no difference. The strong models do better on the
questions about Roman life. Thus the second type of question is not only more
easy.

## category-knowledge

This graph shows the accuracy for each subject. The bar shows the mean of all
the models. The diamond shows the model that has the best accuracy. The number
after the name of the subject shows how many questions the bar uses.

A subject that has less than six questions is not accurate enough to show
alone. All of these subjects are together in one row.

## co-failure

This graph shows if two models fail on the same questions. Each square shows
the phi correlation for two models. The phi correlation compares the results of
the two models for each question.

A dark blue square shows that the two models agree. A pale square shows that
the two models do not agree. A red square shows an opposite result. The
diagonal is empty, because a model always agrees with itself.
