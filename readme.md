<h1> Speech detection of real-time MRI vocal tract data </h1>

In this project, <a href="https://figshare.com/articles/dataset/A_multispeaker_dataset_of_raw_and_reconstructed_speech_production_real-time_MRI_video_and_3D_volumetric_images/13725546/1">real-time MRI data</a> was applied to recognize spoken letters from tongue movements using a vector-based image detection approach. In addition, to generate more data randomization was applied by minimally rotating the vectors. The pixel vectors of a video clip during which a certain letter was spoken could then be passed into a Deep Learning model. For this purpose, the neural networks LSTM and 3D-CNN were used and studied for their performance.

![image](https://user-images.githubusercontent.com/73224461/231983799-55e01ad7-fa02-4aa8-a084-58976a90ed6d.png)

*Data sctructure*

As shown in the Figure video (mp4), recon (h5) and stimmuli (pptx) were used in this work. Video and stimmuli were used to manually extract and label timeframes of spoken vocals in csv files.

**Where should you keep your data files?
In "data/sub*xy*/*files and folders*
