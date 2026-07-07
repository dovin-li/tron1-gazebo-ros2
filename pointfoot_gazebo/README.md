# TRON1 导航系统

## 软件版本

| 组件 | 版本 |
|------|------|
| 操作系统 | Ubuntu 22.04 (Jammy) |
| ROS2 | Humble (2026.06.12) |
| nav2 | 1.1.20 |
| slam_toolbox | 2.6.10 |
| Gazebo | Classic (libgazebo_ros2_control) |
| Python | 3.10 |
| ONNX Runtime | 策略加速 |

## 依赖项

```bash
# ROS2 Humble (完整安装)
sudo apt install ros-humble-desktop

# nav2 导航栈
sudo apt install ros-humble-nav2-bringup ros-humble-nav2-amcl ros-humble-nav2-map-server \
  ros-humble-nav2-planner ros-humble-nav2-controller ros-humble-nav2-bt-navigator \
  ros-humble-nav2-behaviors ros-humble-nav2-lifecycle-manager ros-humble-nav2-costmap-2d \
  ros-humble-nav2-dwb-controller ros-humble-nav2-navfn-planner ros-humble-navigation2

# SLAM
sudo apt install ros-humble-slam-toolbox

# 手柄 / 传感器
sudo apt install ros-humble-joy ros-humble-pointcloud-to-laserscan ros-humble-tf2-tools

# Gazebo
sudo apt install ros-humble-gazebo-ros2-control ros-humble-gazebo-ros-pkgs

# Python (仿真 Web 遥控)
pip install flask
```

## 项目结构

```
pointfoot_gazebo/
├── launch/
│   ├── empty_world.launch.py      # 仿真 Gazebo 启动
│   ├── slam_sim.launch.py         # 仿真建图 (ground_truth_odom)
│   ├── slam_real.launch.py        # 真机建图
│   ├── nav_sim.launch.py          # 仿真导航 (map→odom TF)
│   └── nav_real.launch.py         # 真机导航
├── config/
│   ├── nav2_params.yaml           # 导航参数
│   ├── slam_params.yaml           # SLAM 参数
│   ├── navigate_to_pose.xml       # 导航行为树
│   ├── navigate_through_poses.xml # 途经点行为树
│   ├── tron1_slam.rviz            # 建图 rviz 界面
│   └── tron1_nav.rviz             # 导航 rviz 界面
├── scripts/
│   ├── sim/                       # 仿真专用
│   │   ├── ground_truth_odom.py   # Gazebo 真值里程计
│   │   └── joy_bridge.py          # 手柄→cmd JSON
│   ├── real/                      # 真机部署
│   │   └── cmd_vel_bridge.py      # nav2 /cmd_vel→JSON
│   ├── common/                    # 共用
│   │   ├── tron1_ctrl.py          # ONNX 控制器
│   │   └── tron1_web.py           # Web 遥控界面
│   └── launch_scripts/            # 一键启动脚本
│       ├── tron1_test.sh          # 一键仿真导航测试
│       ├── tron1_slam.sh          # 仿真建图
│       ├── tron1_nav.sh           # 仿真导航
│       ├── tron1_slam_real.sh     # 真机建图
│       └── tron1_nav_real.sh      # 真机导航
├── worlds/empty_world.world       # Gazebo 仿真世界
├── include/ PointFootHWSim.h      # C++ 硬件仿真接口
├── src/     PointFootHWSim.cpp    # C++ 硬件仿真实现
├── CMakeLists.txt
├── package.xml
└── README.md
```

## 仿真部署流程

### 1. 获取代码
```bash
export ROBOT_TYPE=PF_TRON1A
mkdir -p ~/limx_ws/src
cd ~/limx_ws/src
git clone https://github.com/ShunChuang-Tech/nav-on-tron1-ros2.git tron1-gazebo-ros2
# 还需从 LimX 官方仓库获取: robot-description, limxsdk-lowlevel, tron1-rl-deploy-python
```

### 2. 编译
```bash
cd ~/limx_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

### 3. 建图
```bash
bash pointfoot_gazebo/scripts/launch_scripts/tron1_slam.sh
# rviz 里看到地图实时生成
# 浏览器 http://<IP>:8080 遥控机器人
# 建完保存:
ros2 run nav2_map_server map_saver_cli -f ~/maps/tron1_map
```

### 4. 导航测试 (一键)
```bash
bash pointfoot_gazebo/scripts/launch_scripts/tron1_test.sh
# 自动: Gazebo → 控制器站稳 → 导航激活
# rviz: 2D Pose Estimate → Nav2 Goal
```

或分步:
```bash
# 第一步: 仿真环境 + 机器人站立
bash pointfoot_gazebo/scripts/launch_scripts/tron1_slam.sh
# 机器人站好后 Ctrl+C 关掉 SLAM (Gazebo+控制器保留)

# 第二步: 导航
bash pointfoot_gazebo/scripts/launch_scripts/tron1_nav.sh
```

## 真机部署流程

### 前置条件
- TRON1 真机已上电
- ROS2 Humble 环境已配置
- 雷达 (Mid-360S) + 里程计已运行
- 已建好地图文件 `~/maps/tron1_map.yaml`

### 安装
```bash
git clone https://github.com/ShunChuang-Tech/nav-on-tron1-ros2.git
cd tron1-gazebo-ros2
colcon build --symlink-install
```

### 建图
```bash
bash pointfoot_gazebo/scripts/launch_scripts/tron1_slam_real.sh
# 保存: ros2 run nav2_map_server map_saver_cli -f ~/maps/tron1_map
```

### 导航
```bash
bash pointfoot_gazebo/scripts/launch_scripts/tron1_nav_real.sh
# rviz: 2D Pose Estimate 定初始位姿 → Nav2 Goal 发目标
```

## 系统架构

```
传感器 (/scan + /scan3d)
    ↓
代价地图 (local_costmap + global_costmap)
    ↓                          ↓
全局规划 (NavfnPlanner)    局部规划 (DWBLocalPlanner)
    ↓                          ↓
行为树 (navigate_to_pose.xml)
    ↓
bt_navigator → controller_server → /cmd_vel
    ↓
cmd_vel_bridge → /tmp/tron1_cmd.json
    ↓
ONNX 控制器 → 关节指令
```

| 模块 | 插件 | 说明 |
|------|------|------|
| 全局规划 | nav2_navfn_planner/NavfnPlanner | Dijkstra, 0.5m 容差 |
| 局部规划 | dwb_core::DWBLocalPlanner | 7 critic, max 0.26m/s |
| 定位 | AMCL (likelihood_field) | 差分运动模型 |
| 代价地图 | static + obstacle/voxel + inflation | scan + scan3d 双源 |
| 行为 | Spin / BackUp / Wait / DriveOnHeading | behavior_server |
| 行为树 | ComputePathToPose → FollowPath | 自定义 XML |

**Lifecycle 激活顺序**: map_server → amcl → controller_server → planner_server → behavior_server → bt_navigator

## 常见问题

### 机器人往前冲 / 摔倒
编码器漂移 (仿真特有问题):
```bash
ros2 service call /pause_physics std_srvs/srv/Empty
kill -9 $(pgrep -f tron1_ctrl.py)
sleep 2
python3 pointfoot_gazebo/scripts/common/tron1_ctrl.py &
sleep 5
ros2 service call /unpause_physics std_srvs/srv/Empty
```

### 导航不工作 (看不到路径)
1. 确认 AMCL 已定位: rviz → 2D Pose Estimate 标位置
2. 确认已发目标: rviz → Nav2 Goal 标目标
3. 检查 lifecycle: `ros2 lifecycle list /bt_navigator`
4. 检查桥接: `ps aux | grep cmd_vel_bridge`

### ros2 daemon 找不到节点
```bash
ros2 daemon stop; sleep 1; ros2 daemon start
```

## 后期优化 (待做)
- SmootherServer — 全局路径平滑
- WaypointFollower — 多路点巡逻
- TEB/RPP 控制器 — 替代 DWB
