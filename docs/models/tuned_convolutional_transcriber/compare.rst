Example image with transcriptions
=================================

.. figure:: compare.png
   :width: 95%
   :align: center
   :figwidth: 95%

   On the left, a test image from the benchmark (not part of the training dataset). On the right, the most-likely digit in each location from the tuned convolutional transcriber after 50 epochs training. Digits in blue are correct, in red mistakes.

Code to make figure

.. literalinclude:: ../../../models/ATB2_retuned/validation/compare_images.py

