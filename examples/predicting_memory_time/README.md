# Hints and Tools for monitoring your jobs 

The main point of this README is to provide you with the tools and knowledge of understanding where the main cause of increasing memory, CPU time, and GPU memory is likely to come from in your code that you submit as a job on the HEC:

1. The case of tagging, using a machine learning model to infer/predict on data, or training machine learning models the time and memory requirements will be dependent on the **batch size** which is the amount of data you tag or train from in one go. The larger the batch size the more memory will be required, but the quicker the model should run/train. **Note** if your are processing/training on data that can vary in size e.g. text each batch size may contain, for instance, 32 sentences but those 32 sentences are very likely to vary in length thus the longer the sentences are the more memory is required to process them (this only really applies to deep learning methods that represent sentences as sequence of varying word lengths, if using a bag of words model/representation this problem can be ignored.).
2. The case of Bag Of Words (BOW) model for Natural Language Processing (NLP) I would suspect the main memory requirement (not sure about time but I would suspect time as well) will be based on the size of your BOWs e.g. if you are going to represent all words in your BOW vector or just the top 100 words, the more words you represent the more memory you will require.
3. For deep learning models e.g. RNNs, Transformers, etc when training them the memory requirements (if you cannot fit everything into a the batch size you want you have to [accumulate the gradients](https://medium.com/huggingface/training-larger-batches-practical-tips-on-1-gpu-multi-gpu-distributed-setups-ec88c3e51255) thus taking longer to train.) will be based on the number of parameters in your model, which is mainly based on the hidden sizes of your model. Knowing some of the differences between the models is useful e.g. transformers increase in computation non-linearly with the number of words whereas RNN based models increase non-linearly with the dimension of the hidden size see [table 1 of Attention Is All You Need, Vaswani et al. 2017](https://arxiv.org/pdf/1706.03762.pdf). A good guide for understanding transformers is by [Jay Alammar](https://jalammar.github.io/illustrated-transformer/), [for RNN and CNN Stanford has a good overview](https://stanford.edu/~shervine/teaching/cs-230/cheatsheet-recurrent-neural-networks), and another good overview of [RNN specifically LSTM Christopher Olah.](https://colah.github.io/posts/2015-08-Understanding-LSTMs/)

## Table of contents

1. [Tools](#tools)
2. [Examples showing how to use the tools](#examples-showing-how-to-use-the-tools)

## Tools

Some tools for discovering the amount of memory, CPU time, and transfer of data being used. For tools looking at the amount of memory used in the majority of cases we are mainly interested in the peak amount of memory used as we want to determine how much memory is required to run the job/code and thus determine how much memory we need to request for that job:

1. **Linux and Mac** you can use the Python Native [resource library](https://docs.python.org/3.7/library/resource.html), which uses the `getrusage` command from the underlying OS, the [man page can be found here](https://man7.org/linux/man-pages/man2/getrusage.2.html). The main memory statistic that is of use is the peak memory used to get this in **KB** for Linux and **Bytes** for Mac (this my change over time so check the man pages for `getrusage` on your OS) run at the end of your script:
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
6. Keeping track of GPU usage there are various tools that you can use, of which the [fastai docs have a great guide on these various tools.](https://docs.fast.ai/dev/gpu.html#pynvml) The one tool to highlight for Python is the [pynvml](https://pypi.org/project/nvidia-ml-py3/) library as it can quickly query the GPU without having to call `nvidia-smi`. At the current moment I do not know of a tool that outputs peak memory usage of the GPU, I know that PyTorch has various functions for [max_memory_allocated](https://pytorch.org/docs/stable/cuda.html#torch.cuda.max_memory_allocated) and [max_memory_reserved](https://pytorch.org/docs/stable/cuda.html#torch.cuda.max_memory_reserved), but these functions [do not take into account the memory required to run PyTorch on the GPU which can be 0.5GB](https://docs.fast.ai/dev/gpu.html#unusable-gpu-ram-per-process).

### Recommendations

1. Use either [resource library](https://docs.python.org/3.7/library/resource.html) (for windows [psutil library](https://github.com/giampaolo/psutil)) to find an accurate measure of peak memory used compared to just relying on the [Scalene library](https://github.com/emeryberger/scalene). I find that all other features of Scalene like *Net (MB)* to be accurate.
2. Using a tool like [pynvml](https://pypi.org/project/nvidia-ml-py3/) for GPU memory monitoring compared to the information that is generated for you from the HEC about the GPU usage, see the [Comparing Results section in the GPU example for more details why.](./gpu_example/README.md#comparing-results).

## Examples showing how to use the tools

1. Example of how to use the [resource library](https://docs.python.org/3.7/library/resource.html) and the Python [time library](https://docs.python.org/3.7/library/time.html) to find the maximum amount of memory required for a tagging task and the average time it will take to process a batch. Code can be found at [./resource_and_time_example/README.md](./resource_and_time_example/README.md).
2. Example of how to use Scalene can be found at [./scalene_example/README.md](./scalene_example/README.md).
3. Example of how to use [pynvml](https://pypi.org/project/nvidia-ml-py3/), can be found at [./gpu_example/README.md](./gpu_example/README.md). In this example we run Stanza on the GPU and show how you can find peak GPU memory usage and other GPU memory information. Further we show that you cannot estimated the GPU memory usage through RAM usage on a CPU version of the model.