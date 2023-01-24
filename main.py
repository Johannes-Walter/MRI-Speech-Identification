import h5py
import matplotlib.pyplot as plt

f = h5py.File("MRI_dataset.h5", "r")
dset = f["recon"]
timespan = f["lambda_t"][0][0] * 100


skipped_frames = 10
framecount = len(dset) // skipped_frames

frames = []
fig = plt.figure()
for i in range(0, min(skipped_frames, 1)*framecount, min(skipped_frames, 1)):
    frames.append([plt.imshow(dset[i], cmap="gray", animated=True)])

# print(frames)
from matplotlib.animation import FuncAnimation, ArtistAnimation

ani = ArtistAnimation(fig, frames, interval=timespan*(skipped_frames+1))
ani.save("video.gif")
