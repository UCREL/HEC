# Hints and Tools for monitoring your jobs 

The main point of this README is to provide you with the tools and knowledge of understanding where the main cause of increasing memory, CPU time, and GPU memory is likely to come from:

1. The case of tagging, using a machine learning model to infer/predict on data, or training machine learning models the time and memory requirements will be dependent on the **batch size** which is the amount of data you tag or train from in one go. The larger the batch size the more memory will be required, but the quicker the model should run/train. **Note** if your are processing/training on data that can vary in size e.g. text each batch size may contain, for instance, 32 sentences but those 32 sentences are very likely to vary in length thus the longer the sentences are the more memory is required to process them (this only really applies to deep learning methods that represent sentences as sequence of varying word lengths, if using a bag of words model/representation this problem can be ignored.).
2. The case of Bag Of Words (BOW) model for Natural Language Processing (NLP) I would suspect the main memory requirement (not sure about time but I would suspect time as well) will be based on the size of your BOWs e.g. if you are going to represent all words in your BOW vector or just the top 100 words, the more words you represent the more memory you will require.
3. For deep learning models e.g. RNNs, Transformers, etc when training them the memory requirements (if you cannot fit everything into a the batch size you want you have to [accumulate the gradients](https://medium.com/huggingface/training-larger-batches-practical-tips-on-1-gpu-multi-gpu-distributed-setups-ec88c3e51255) thus taking longer to train.) will be based on the number of parameters in your model, which is mainly based on the hidden sizes of your model. Knowing some of the differences between the models is useful e.g. transformers increase in computation non-linearly with the number of words whereas RNN based models increase non-linearly with the dimension of the hidden size see [table 1 of Attention Is All You Need, Vaswani et al. 2017](https://arxiv.org/pdf/1706.03762.pdf). A good guide for understanding transformers is by [Jay Alammar](https://jalammar.github.io/illustrated-transformer/), [for RNN and CNN Stanford has a good overview](https://stanford.edu/~shervine/teaching/cs-230/cheatsheet-recurrent-neural-networks), and another good overview of [RNN specifically LSTM Christopher Olah.](https://colah.github.io/posts/2015-08-Understanding-LSTMs/)

## Tools

Some tools for discovering the amount of memory, CPU time, and transfer of data being used. For tools looking at the amount of memory used in the majority of cases we are mainly interested in the peak amount of memory used as we want to determine how much memory is required to run the job/code and thus determine how much memory we need to request for that job:

1. **Linux and Mac** you can use the Python Native [resource library](https://docs.python.org/3.7/library/resource.html), which uses the `getrlimit` command from the underlying OS, the [man page can be found here](https://man7.org/linux/man-pages/man3/vlimit.3.html). The main memory statistic that is of use is the peak memory used to get this in **KB** for Linux and **Bytes** for Mac (this my change over time so check the man pages for `getrlimit` on your OS) run at the end of your script (this is what we used in the [./example/tagging.py](./example/tagging.py) script):
``` python
from resource import getrusage, RUSAGE_SELF
getrusage(RUSAGE_SELF).ru_maxrss
``` 
2. **Windows** you can use the [psutil library](https://github.com/giampaolo/psutil), installed via pip `pip install psutil` or conda `conda install psutil`, with the command at the end of your script:
``` python
import psutil
print(psutil.Process().memory_info().peak_wset)
```
3. If you want to know how long a single batch takes to run wrapping it around a timing function should be all you need, as shown with this:
``` python
import time
import spacy

nlp = spacy.load("en_core_web_sm", disable=[ "tagger", "parser"])
data = ['a batch', 'of data']

start_time = time.perf_counter()

for processed_data in nlp.pipe(data):
    continue

end_time = time.perf_counter()
print(end_time - start_time)
```
4. For more information on how to incorporate timing functions into your code see the [real python blog post](https://realpython.com/python-timer/). To get a more accurate measure of how long your code takes to run you could use the [timeit](https://docs.python.org/3/library/timeit.html#python-interface) interface which runs a block of code *N* times (default *N* = 1000) and reports how long the code took to run *N* times. An example of how to use the `timeit` function with repeat is shown below (repeat means that the code is run *N* * *M* times where *N*=100 and *M*=3 in this case and reports how long it took to run the code *N* times for each *M*), the [Python documentation states that you should use the minimum reported time](https://docs.python.org/3/library/timeit.html#timeit.Timer.repeat) as the time to report. For a [good guide on how to use the timeit function see this blog](https://www.pylenin.com/blogs/python-timeit-module/#using-timeit-with-python-functions-with-arguments):
``` python
import timeit

setup_code = '''
import spacy

nlp = spacy.load("en_core_web_sm", disable=[ "tagger", "parser"])
data = ["a batch", "of data"]
'''

code_to_run = '''
for processed_data in nlp.pipe(data):
    continue
'''

print(timeit.repeat(stmt=code_to_run, setup=setup_code, number=100, repeat=3))
# In my case this prints:
# [0.1814169869903708, 0.18344234900723677, 0.17951916699530557]
```
5. **All OS** (for Windows it states it runs on Ubuntu in Windows [WSL2](https://docs.microsoft.com/en-us/windows/wsl/install-win10)) another tool is a profiler of which [Scalene library](https://github.com/emeryberger/scalene) has been recommended. Can be installed through pip e.g. `pip install scalene`. A profiler analysis your code line by line to show you which lines are using the most memory, CPU time, and transfer of data. Profilers are useful as they can show which lines of code are using up the most resources, this can then allow you to potentially improve your code. An example of how to use the `scalene` profile and the output of the profiler can be found in [./scalene_example/README.md](./scalene_example/README.md).

With all of these tools some can be useful when running your main code program rather than a test program to determine how much memory or time it is going to take. You shouldn't run a profiler like `scalene` when running your main code as it will just slow down your program, whereas it would be useful to log every *N* batches how long your program has taken to run those *N* batches whether that is for tagging data or training a machine learning model so that you can get a better idea on when your code is going to finish.

### Recommendations

1. Use either [resource library](https://docs.python.org/3.7/library/resource.html) (for windows [psutil library](https://github.com/giampaolo/psutil)) to find an accurate measure of amount of memory used compared to just relying on the [Scalene library](https://github.com/emeryberger/scalene). I have found memory reporting issues with Scalene when I used it on my Mac laptop, the issue was worse when I installed SpaCy through Conda forge rather than pip.

## Examples showing how to use the tools

1. Example of how to use the 
1. Example of how to use Scalene can be found at [./scalene_example/README.md](./scalene_example/README.md).






















In this example we will show how to roughly predict the amount of memory and compute time that is required for a job. This is useful to know as many of the jobs that you will submit to the HEC will required more than 500MB of memory, which is the [default max memory size](https://answers.lancaster.ac.uk/display/ISS/Running+large+memory+jobs+on+the+HEC) of a single node CPU job. The compute time is useful in general so that you know roughly how long a job may take.

As specified in the [running large memory jobs on the HEC](https://answers.lancaster.ac.uk/display/ISS/Running+large+memory+jobs+on+the+HEC) you need to specify in the job script (script with the `.com` extension) the max amount of memory required if you want to use more than 500MB.

This example will show case how you can roughly find out the memory requirements of your job, using only the HEC and not your own computer.

## Tagging data as the example use case

This example is some what based on this [blog post](https://pythonspeed.com/articles/estimating-memory-usage/) by Itamar Turner-Trauring, the blog post is more detailed and easier to follow I think, but this example is tailored to Natural Language Processing.

The task this example is going to be based on is **tagging data** using SpaCy, whereby in this example we are going to find all of the Named Entities using the English SpaCy small Named Entity Recognizer (NER) model in the book Alice in wonderland. The Alice in wonderland text can be found at [./example/alice-in-wonderland.txt](./example/alice-in-wonderland.txt) (this was downloaded from [project Gutenberg](https://www.gutenberg.org/ebooks/11)). The full code for this example can be found at [./example/tagging.py](./example/tagging.py) and the Conda install environment file [./example/environment.yaml](./example/environment.yaml).

The main objective of this is to determine how much memory we think we will need if we are going to either tag up the whole book (I know this can be done easily as the book is small but this is somewhat a toy example) or if this book is typical of a collection of books and thus later on going to tag many books using the same method but modifying the code so that it loops over a collection of books rather than just the one.

The main component in this example that will determine how long in time and how much memory it will take to tag the book is the `batch size`, the batch size is the amount of text (in this case the amount of text is determined by number paragraphs) that will be processed by the NER model in one go. The script [./example/tagging.py](./example/tagging.py) allows us through command line arguments to:

1. Process the whole text (`text`) or just a batch (`batch`), **OR** find the number of paragraphs in the text without any NER processing (`number_paragraphs`).
2. The size of the batch e.g. `50` whereby 50 here means we will process 50 paragraphs of text in one go. 

Given this we should be able to roughly figure out the amount of memory and the time it will take to process the whole text by only processing one batch of the text with a given batch size. To test this we will use the [./example/tagging.py](./example/tagging.py) and the alice in wonderland text perform some experiments on the HEC showing this, to do so:

1. Transfer the [./example](./example) directory to your home directory on the HEC: `scp -r example/ username@wayland.hec.lancaster.ac.uk:./`
2. Create the conda environment with the relevant python dependencies and download the SpaCy English model. This can be done by submitting the [./example/install.com](./example/install.com) job e.g. `qsub install.com`
3. We can now run the [./example/memory_time.sh](./example/memory_time.sh) script which will state the number of paragraphs in the Alice text, and then run the script over one batch of size 50, 100, and 150 and then to finish the whole text. The script will then print out the time it takes for each batch (or in the last case to process the whole text) to process and the peak amount of memory used. To run the script submit the following job `qsub process.com`
4. After the job has finished within the output file in my case it is `time-memory.o6575917` it should contain something similar to the following below `cat time-memory.o6575917`:
``` bash
Number of paragraphs in text: 881
Script arguments: process number_paragraphs and batch size 0
Peak amount of memory used: 91.84 MB
Time taken: 0.15294885635375977
-------------End of Script------------

Script arguments: process batch and batch size 50
Peak amount of memory used: 115.624 MB
Time taken: 0.15895438194274902
-------------End of Script------------

Script arguments: process batch and batch size 100
Peak amount of memory used: 146.656 MB
Time taken: 0.26904869079589844
-------------End of Script------------

Script arguments: process batch and batch size 150
Peak amount of memory used: 166.828 MB
Time taken: 0.37573981285095215
-------------End of Script------------

Script arguments: process text and batch size 50
Peak amount of memory used: 123.848 MB
Time taken: 1.7628285884857178
-------------End of Script------------
```

We can see from this Alice in wonderland contains 881 paragraphs and that each time we increase the batch size by 50 it adds between 31 and 20MB of memory but with the batch size increasing the time taken per paragraph decreases e.g. batch size 150 = ~0.0025s, 100 = ~0.0026s, and 50 = ~0.0025s. The prediction of running the whole text with a batch size of 50 using 115.624MB of memory was fairly close, 123.848MB. The time prediction was a fair bit of though as multiplying the time taken for one batch of 50 = 0.1529s multiplied by the number of batches in the whole text = (881/50 = 18) is (18 * 0.1529 = 2.75s) which is 56% more than the actually time it took of 1.76s.

The reason for the differences in time and memory is most likely due to batches containing paragraphs of varying length e.g. the first batch might contain paragraphs that are on average a bit smaller thus not requiring as much memory and not taking as long to process as the average batch.

From this we can see that if we predicting that the memory we required to process the whole text is 115.624MB for a batch size of 50 we probably want to add some more memory just in case, to be generous I would like at least 50% more memory than I think I need in doing so you know you should be somewhat safe. Even though our time prediction was out by 56%, this estimate could have been better if we ran several batches of 50 to get a more accurate time estimate but this takes more initial time which could be better spent running the main experiment (in this case run the NER over the whole book).

You should notice a new file called `Alice-Entities.tsv` which contains the Named Entities found in the Alice in wonderland book with the first two entries being:
```tsv
0	Wonderland	GPE	54	64
0	Lewis Carroll	PERSON	69	82
```