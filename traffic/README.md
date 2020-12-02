First attempt: -Convolutional layer with 32 filters 
               -Max pooling layer with 2x2 pool size
               -Hidden layer with 128 units and a 0.5 dropout
               
               
Second attempt : Max pooling layer with 3x3 pool size and dropout changed to 0.4 
results: 3x3 pool size didnt work well

third attempt: Pool size down to 2x2 again, added a new convolutional layer with 32 filters after the pooling layer
results: accuracy in 95%, but it took twice the time to compile

four attempt: the second convolutional layer was increased in numbers of filters from 32 to 64
results: it got really slow but the accuracy was almost 90% in the second epoch. It finished with 95% of accuracy,
the same as before, but took too long to finish. 10 epochs was unnecessary

