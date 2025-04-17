# 🔍 What is SVM?

Support Vector Machine (SVM) is a supervised machine learning algorithm that can be used for both classification and regression tasks, but it's mostly used for classification.

## Core Idea:

SVM tries to find the best boundary (hyperplane) that separates data points of different classes with the maximum margin.

![image](https://github.com/user-attachments/assets/3aa16d90-75b5-4aee-9295-92bddc88a331)


# 🧠 Why Use SVM?

* Works well for high-dimensional spaces.

* Effective in non-linear classification using kernel tricks.

* Strong theoretical foundation and often yields high accuracy.

* Can handle both linear and non-linear classification.

## 📐 How Does SVM Work?

**1. Linear SVM (Linearly Separable Data)**
   
* Imagine two classes of points.

* SVM finds the best line (in 2D) or hyperplane (in higher dimensions) that separates them with the maximum margin.

* Support Vectors are the data points closest to the hyperplane. They “support” or define the boundary.


**2. Non-Linear SVM**
   
* What if data is not linearly separable?

* SVM uses a trick called the Kernel Trick to map data into a higher-dimensional space where a linear separation is possible.

# 🎯 Kernel Trick

**What is a Kernel?**

A kernel function transforms the data into a higher-dimensional space without explicitly computing the coordinates in that space.

![Screenshot 2025-04-17 152450](https://github.com/user-attachments/assets/60817563-5b03-473f-b10f-1c90ac0afbf7)

