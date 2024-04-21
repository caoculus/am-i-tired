## Inspiration
There are many moments where we are tired but we don't feel it mentally. However, using machine learning and computer vision, we can tell if we actually need rest or not from webcam video of facial features.

## What it does
From a short video, the web app can detect and respond to how tired you currently are from a scale of 1 - 10, it is easy to use and straight to the point.

## How we built it
The frontend is built with vuejs, vite, and typescript using  Tailwindcss and PrimeVue component library. The backend is built with rust. It uses an Axum server with websocket communication.
The machine learning pipeline has two components. The face detection and localization is done with YOLOv8 architecture, and the drowsiness detection is done with a vision transformer model. Due limited labelled data, all models are finetuned from pretrained models on very large datasets.
## Challenges we ran into
First was figuring out how to consistently send data stream over the internet, which couldn't be done with traditional http requests, thus we came across websocket. The machine learning suffered from lack of high quality data. Pretrained models helped, but we also suspect that the validation split of some datasets may be contaminated.

## Accomplishments that we're proud of
We made the app work and deployed on the internet along with 98.6% accuracy on the validation set*.

## What we learned
VueJS, and modifying attention in library files to use flash attention instead :)

## What's next for Am I Tired (AIT)
1. Add user validation
2. Saving the results and their time of date
3. User login and saving it in database
4. Results will be displayed for each user
5. Add additional notes to each result
6. Collect custom data, and download a large dataset from baidu
7. Experiment with neural architecture search and advanced hyper-parameter tuning methods  

You can try out the web app yourself through this link: https://am-i-tired.fly.dev
