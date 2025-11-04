# 🦾 Hybrid Control for Mecanum Robots: Navigation with TD3 & MediaPipe Gestures

A hybrid reinforcement learning and gesture-driven control system for autonomous Mecanum robots, combining Twin Delayed DDPG (TD3) with MediaPipe for efficient and intuitive warehouse navigation.

----
### 🚀 Overview

This project presents a hybrid robotic control framework for warehouse automation that seamlessly integrates autonomous navigation via Twin Delayed Deep Deterministic Policy Gradient (TD3) with human-in-the-loop gesture control using Google MediaPipe.

The system enables a Mecanum-wheeled robot to:

- Navigate autonomously using reinforcement learning, adapting to dynamic layouts and obstacles.

- Respond to real-time hand gestures, enabling intuitive manual overrides by warehouse personnel.

This combination enhances operational flexibility, safety, and efficiency in complex industrial settings.


<p align="center">
  <img src="IMG_4956.jpg" alt="" width="800"/>
</p>


🛠️ **Built entirely from scratch** — from mechanical assembly and hardware wiring to computer vision pipeline and control logic — as part of a Reinforcement Learning & Robotics course capstone.

----
### 🧠 Problem Motivation

Modern warehouses demand adaptive and intelligent automation capable of handling unpredictable layouts and human interactions.
Traditional path-planning algorithms (A*, Dijkstra, etc.) lack adaptability to dynamic changes, while manual control reduces efficiency.

This project bridges the gap through a hybrid autonomy approach, combining:

- TD3’s policy-based reinforcement learning for optimized motion planning.

- MediaPipe’s vision-based gesture recognition for seamless human intervention.                            

----

## 🧩 System Architecture


----

### ⚙️ Technical Stack

| Layer         | Technology                  | Purpose                     |
| ------------- | --------------------------- | --------------------------- |
| RL Framework  | PyTorch                     | TD3 model training          |
| Simulation    | ROS2, Gazebo                | Environment & robot control |
| Vision        | OpenCV, MediaPipe           | Hand gesture recognition    |
| Hardware      | Raspberry Pi, Mecanum Robot | Physical control            |
| Visualization | TensorBoard, RViz           | Performance tracking        |


----

## Implementation

### 1. Gesture-Based Control (MediaPipe)

**Framework:** Google MediaPipe + OpenCV  
**Method:** Hand landmark tracking and gesture classification  
**Hardware:** Raspberry Pi motor controller using GPIO + PWM  

**Mapping Logic:**

| Gesture | Action |
| :------: | :------ |
| ✊ Closed Fist | Stop |
| ☝️ 1 Finger | Move Forward |
| ✌️ 2 Fingers | Slow Down |
| 🤟 3 Fingers | Turn Left |
| 🖖 4 Fingers | Turn Right |

MediaPipe computes **inter-landmark distances** to classify gestures, while OpenCV provides **real-time visual feedback** through camera streams and overlayed hand skeletons.

---

### 2. Autonomous Navigation (TD3 in ROS2)

**Algorithm:** Twin Delayed Deep Deterministic Policy Gradient (TD3)

**Key Components:**
- **Actor-Critic Architecture** with delayed policy updates and target smoothing  
- **Replay Buffer** for experience sampling  
- **Soft Updates** for stable convergence  
- **Simulation Environment:** Gazebo + ROS2 + Velodyne LiDAR  

**Training Metrics:**
- 📈 **Average Q-Value ↑** (stabilized after 30k steps)  
- 🚫 **Collision Rate ↓** over training episodes  

---

### Core Equations

The TD3 algorithm optimizes the critic and actor networks based on the following objective functions:

$$
Q_{\pi}(s, a) = \mathbb{E}\left[ r_t + \gamma Q_{\pi}(s_{t+1}, \pi(s_{t+1})) \right]
$$

Critic loss function:

$$
L(\theta_Q) = \frac{1}{N} \sum \left( Q_{\theta_Q}(s, a) - y \right)^2
$$

Where the target value \( y \) is computed as:

$$
y = r + \gamma \min_{i=1,2} Q_{\theta_i'}(s', \pi'(s'))
$$

---

🧠 **Insight:**  
TD3 mitigates overestimation bias common in DDPG by using *clipped double Q-learning* and *target policy smoothing*, resulting in more stable training for continuous control tasks such as autonomous navigation in ROS2 environments.


----
### 📸 Real Robot Build

🧩 Fully built and tested — below are snapshots from our final build and live testing sessions.

🎥 [You can watch the video here](https://drive.google.com/file/d/1VRiRxztKW1HbA51uEGdjKxSKgo_ikSBu/view?usp=sharing)


- ✅ Physical robot assembled using custom chassis, motor mount, and onboard camera.

  <p align="center">
  <img src="97e1fbd5-4bbb-4b26-8b59-cd101058960d.jpg" alt="" width="500"/>
</p>


- ✅ Controlled entirely via visual input — no manual remote or wired control.
  
----

### 📈 Experimental Results

| Metric               | Before Training | After Training | Improvement |
| -------------------- | --------------- | -------------- | ----------- |
| Avg. Q-Value         | 45.2            | 121.8          | +170%       |
| Collision Rate       | 0.35            | 0.08           | -77%        |
| Task Completion Time | 118s            | 63s            | -47%        |


----



