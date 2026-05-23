# **破局“内存墙”与“互联墙”：AI基础设施接口互联领域的痛点分析与创业方向深度调研**

随着前沿人工智能大语言模型（LLM）的参数量突破万亿级别，以及混合专家模型（MoE）在架构设计中的广泛采用，全球数据中心的底层硬件基础设施正面临着一场由算力狂飙引发的系统性危机。在过去的二十年里，服务器硬件的峰值浮点运算能力（FLOPS）持续以惊人的幅度扩展，然而，内存带宽与系统内部互联速率的增长步伐却远远落后于计算能力的跃升 1。这种算力与数据传输能力之间日益扩大的剪刀差，导致系统性能的瓶颈正加速从传统的“计算受限”向“内存受限”及“通信受限”发生不可逆转的转移。  
在这一宏观产业背景下，以Astera Labs为代表的接口互联芯片企业，凭借其在解决高速信号物理衰减与重构集群组网拓扑方面的创新硅片及软件方案，不仅实现了自身的商业成功，更指明了下一代数据中心架构的演进方向。本报告将以当前AI基础设施领域的硬件互联痛点为切入点，深度剖析行业标杆企业与底层互联协议的解题思路，并结合诸如CXL、UALink、UEC、UCIe等前沿互联标准，以及硅光技术（Silicon Photonics）与共封装光学（CPO）的最新突破，为学术研究与创新创业提供具备极高颗粒度、有理有据的深度洞察与战略方向指引。

## **一、 当前AI集群互联架构的核心物理与系统痛点分析**

在分布式训练与超大规模推理场景中，AI基础设施正面临多维度、深层次的物理与架构限制。通过对底层硬件生态及近期产业数据的深度剖析，可以将当前行业面临的核心痛点归结为以下四个关键维度。

### **1.1 “内存墙”危机与生成式AI的KVCache容量瓶颈**

人工智能模型的训练与推理对内存容量和带宽的依赖程度正在急剧上升，现有的硬件架构已经触及了物理与经济的双重天花板。在LLM的推理过程中，为了支持越来越长的上下文窗口，系统必须在内存中维持庞大的键值缓存（KVCache）。然而，当前GPU板载的高带宽内存（HBM）容量极其有限。更为严峻的是，HBM的供应链受到了极大的制约，据SK Hynix等头部供应商披露，其2026年的全部HBM产能早已售罄，且台积电（TSMC）的CoWoS先进封装产能持续面临极度紧张的局面，这不仅限制了GPU的产量，也导致内存价格大幅飙升，极大地推高了基础设施的成本 2。  
为了弥补昂贵且稀缺的HBM容量，系统架构师通常需要借助CPU的主存（DRAM）来扩展系统总内存，但受限于单路CPU插槽固有的内存通道数量限制，主存的横向扩展性同样存在不可逾越的物理上限 3。现有的基于以太网的远程直接内存访问（RDMA）方案虽然能够在一定程度上实现内存池化，但其复杂的通信协议、多级数据路径以及需要CPU驱动或GPU内部轮询的跨组件同步开销，引入了极高的数据访问延迟 3。这种高延迟架构完全无法满足AI推理对“首Token生成时间”（Time-To-First-Token, TTFT）的严苛要求，导致昂贵的计算资源在等待数据搬运的过程中被大量闲置 3。

### **1.2 摩尔定律减缓、Reticle极限与封装瓶颈**

由于当前光刻设备的“掩膜版极限”（Reticle Limit），单体硅片的物理面积已经达到了制造工艺的天花板，无法通过不断增大单颗芯片的面积来容纳更多的晶体管 5。例如，NVIDIA的Blackwell架构被迫采用双裸片（Dual-die）的“超级芯片”设计，并通过超高速互联链路进行缝合，这标志着高性能应用领域中，庞大的单体处理器时代已经彻底终结 5。  
为了规避物理尺寸限制，业界全面转向了Chiplet（小芯片）架构与3D先进封装技术。然而，高密度的3D逻辑芯片堆叠带来了极度集中的热点，传统的数据中心风冷技术根本无法将这些热量有效散出，迫使运营商加速向液冷或封装内微流控散热技术演进以防止芯片熔毁 5。更为致命的是，类似于16层HBM4等高密度存储堆叠技术的良率在目前阶段仍然在60%左右徘徊，这种因三维堆叠带来的低良率进一步构成了大众市场广泛采用先进封装的巨大成本壁垒 5。

### **1.3 高速信号的物理衰减悬崖与完整性挑战**

随着互联标准向PCIe 6.0及未来的PCIe 7.0演进，信号传输速率分别飙升至64 GT/s和128 GT/s，并全面引入了PAM4（四电平脉冲幅度调制）信令 6。PAM4信令通过四个电压幅度来表示两个比特的信息，虽然在相同带宽下提升了数据吞吐量，但也使得信号对噪声和衰减变得极其敏感。  
在物理层面上，速率的翻倍带来了极端的信号完整性挑战。PCIe 6.0的通道损耗预算被严格限制在32 dB，相比PCIe 5.0的36 dB更为严苛 9。在这样的高频运行环境下，信号的上升时间极短，跃迁幅度受限，传统的铜导线在极短的距离内（通常只有几英寸）就会出现严重的信号畸变。这迫使主板设计必须引入极其复杂的均衡电路与时钟恢复机制，不仅增加了系统的功耗，还限制了AI服务器内部GPU、CPU、网卡之间的物理布局灵活性，更使得跨机架的铜缆长距离互联变得举步维艰 9。

### **1.4 封闭协议的垄断、MoE路由困境与“吵闹的邻居”效应**

目前占据市场主导地位的高性能横向与纵向扩展网络在很大程度上依赖于单一厂商的专有封闭协议（例如NVIDIA的NVLink）。这种封闭的生态系统不仅剥夺了超大规模云服务商（Hyperscalers）在异构计算环境下的采购灵活性，还因为缺乏开放的竞争而拖慢了整个行业互联技术的创新步伐 10。  
从模型架构的角度来看，混合专家模型（MoE）的广泛采用对底层互联网络施加了前所未有的通信压力。在MoE模型中，路由器需要将每个Token动态分配给数百个专家网络中的极小一部分（例如从256个专家中激活8个），而这些被选中的专家通常分布在集群中不同的物理GPU上 11。这要求网络具备极强的多播（Multicast）能力以及极低的网络配置延迟。然而，传统的通用交换机在处理这种动态多播时，配置时间存在严重的“长尾效应”，甚至可能高达数十毫秒，迫使算法工程师在训练时人为限制专家的物理分布范围（例如强制限制路由不超过4个物理节点），这种硬件对软件的妥协直接削弱了模型的核心推理能力 11。  
此外，在传统的通用PCIe交换架构中，为了节省硬件成本，GPU、CPU、网卡（NIC）与固态硬盘（SSD）往往被逻辑分区，但物理上仍然共享同一个交换机核心与仲裁逻辑。这种资源共享导致了严重的“吵闹的邻居”（Noisy Neighbor）效应。例如，当GPU正通过网卡摄取高带宽训练数据时，如果恰好SSD发起大量I/O请求并抢占了交换机的仲裁资源，就会直接阻塞GPU的网络数据流，引发不可预测的延迟抖动，严重拖累整个AI集群的计算效率 11。

## **二、 行业标杆解构：Astera Labs与前沿企业的解题逻辑**

面对上述系统性痛点，Astera Labs作为专注于AI与云基础设施连接半导体领域的先驱，构建了涵盖重定时器、智能线缆、内存控制器与智能Fabric交换机的全面产品矩阵。结合其他前沿互联企业（如Enfabrica、Eliyan、Marvell、MemVerge）的技术布局，我们可以清晰地勾勒出行业解决互联瓶颈的主流工程路径。

### **2.1 物理层的信号延展与智能重构：Aries与Taurus系列**

为了克服PCIe 6.0/CXL 3.0在高速传输下的信号衰减问题，Astera Labs推出了Aries PCIe/CXL Smart DSP Retimers（智能DSP重定时器）。该芯片集成了专门针对严苛AI服务器信道定制的64GT/s PAM4 SerDes与数字信号处理（DSP）技术，能够在极低功耗下将信号传输距离可靠地延长3倍，有效填补了32 dB严苛损耗预算带来的物理鸿沟 6。其采用的小型封装集成了交流耦合电容并支持灵活的时钟模式，极大简化了主板的布线复杂性 6。  
在此基础上，Astera Labs将重定时技术从主板延伸至线缆端，推出了Aries PCIe/CXL Smart Cable Modules（智能线缆模块，SCM）。这些基于有源电缆（AEC）技术的模块，允许在密集的AI机架内部署稳健的PCIe和CXL连线，从而释放了跨机架GPU到GPU的集群拓扑限制 12。  
而在以太网横向扩展领域，机架顶部（ToR）交换机到服务器网卡的连接同样面临速率瓶颈。Astera Labs的Taurus Ethernet Smart Cable Modules旨在替代传统粗重且难以布线的无源铜缆。Taurus支持高达800G（基于100G/Lane PAM4）的以太网速率，允许数据中心使用非常细的（30/32/34 AWG）铜缆实现长达3米的可靠连接 13。相比于通用AEC，Taurus不仅将电缆弯曲半径减半以优化散热气流，更内置了强大的伪随机二进制序列（PRBS）发生器/检查器等深度诊断功能，支持实时的温度、电压遥测以及安全的固件无线更新（OTA），为大规模机队管理提供了无与伦比的便利性 13。

### **2.2 彻底打破“内存墙”：CXL智能内存控制器与软件中间件的融合**

为了打破由于CPU通道限制造成的内存容量天花板，Astera Labs开发了Leo CXL Smart Memory Controllers。这是业界首批专为云服务器打造的支持内存扩展与池化的企业级解决方案 17。Leo控制器不仅支持CXL 2.0协议，能够为每个控制器提供高达2TB的内存容量扩展（使云服务商能够将服务器内存容量扩大1.5倍以上），还提供了端到端的数据完整性保护与服务器级别的定制化RAS（可靠性、可用性、可维护性）功能 17。  
然而，仅仅拥有底层的Leo等CXL硬件并不足以实现透明的内存池化。在软件中间件层面，MemVerge公司展现了极具突破性的创新。MemVerge的Elastic Memory（弹性内存）软件服务能够与CXL内存池系统无缝协同，实时监控应用程序的内存使用热力图。当检测到主机节点的本地DRAM即将耗尽时，Elastic Memory会动态、按需地从CXL共享池中分配内存给主机，从而彻底消除导致应用程序崩溃或性能骤降的Out-Of-Memory (OOM) 错误，解决了集群中内存分配不均导致的“内存搁浅”问题 19。  
在学术验证与极致性能追求方面，基于CXL内存架构的潜力正在被全面挖掘。最新发表的关于Beluga架构的研究详细阐述了CXL如何重塑大语言模型的KVCache管理 3。该研究指出，通过CXL交换机建立共享的大规模内存池，GPU可以直接利用原生的Load/Store指令访问远程内存，彻底消除了传统RDMA架构中CPU驱动所需的多级数据路径、反弹缓冲区（Bounce Buffers）以及复杂的跨组件轮询同步开销 3。测试数据显示，结合了这一架构的Beluga-KVCache系统在vLLM推理引擎中，实现了惊人的89.6%的首Token生成时间（TTFT）缩减，并将整体吞吐量提升了7.35倍，确立了CXL在未来AI推理内存解构中的核心地位 22。此外，MemVerge还推出了Gismo（全局无IO共享内存对象）技术，通过直接映射内存空间，消除了跨节点分布式AI训练中的网络张量拷贝延迟 19。

### **2.3 重构集群通信网络：智能Fabric交换机的多维进化**

在GPU间通信与异构组网层面，传统的通用PCIe交换机已显颓势。Astera Labs的Scorpio Smart Fabric Switches系列通过从零开始的底层重构，树立了AI专属交换机的新标杆。

* **硬件隔离消除“吵闹邻居”：** Scorpio P系列（提供从32通道到320通道的全矩阵配置）摈弃了单体共享核心的设计，转而使用专用的交换核心和独立的仲裁逻辑将GPU/CPU/NIC的“连接岛”与SSD“连接岛”在物理层面彻底隔离。这一创新确保了不同类型的数据流互不干扰，实现了零性能损耗的高带宽传输 11。  
* **硬件加速破解MoE瓶颈：** 针对混合专家模型（MoE）的多播难题，Scorpio X系列（320通道）集成了专属的Hypercast与In-Network Compute（网络内计算）引擎。该交换机支持直接内存语义通信，完全绕过CPU的协议栈开销，将AI集合操作的效率提升了高达2倍，支持单跳连接多达80个加速器，使得路由算法可以在更广阔的物理节点上自由寻找“最优专家”，释放了模型的全部推理潜力 11。  
* **安全与全景遥测：** Scorpio不仅利用COSMOS软件套件提供深度的链路与数据包诊断，加速了故障隔离，还内置了Secure Boot（安全启动）机制。该机制通过不可变的硬件信任根（RoT）对固件、配置及策略元数据进行签名验证，确保了从上电那一刻起，AI集群的网络拓扑与路由状态便不被恶意篡改 11。

除了纯粹的PCIe/CXL交换外，混合网络架构（Hybrid Networking）正成为行业共识。在这个赛道上，Marvell于2026年斥资5.4亿美元完成了对XConn Technologies的收购 2。XConn此前发布了业界首款混合交换芯片Apollo 2，能够在一块硅片上同时处理CXL 3.1与PCIe Gen 6.2流量 26。Marvell借助此次收购推出的Structera S系列260通道交换机，不仅消除了昂贵的多级级联需求，更为其打造挑战NVIDIA互联霸权的统一开放Fabric平台奠定了物理基础 27。  
与之呼应，Enfabrica则通过其刚刚获得1.15亿美元C轮融资的Accelerated Compute Fabric (ACF) 技术另辟蹊径 28。其最新推出的ACF-S Millennium芯片是一款高达3.2 Tbps吞吐量的超级网卡（SuperNIC）。该芯片通过提供多端口800G以太网连接，结合高度弹性的多路径喷射（Multipath Spraying，支持多达32端口的流量喷射）技术，在横向扩展网络中构建了极具容错性的并发数据通道。这种非点对点、多路径冗余的设计，不仅为GPU、CPU和CXL内存端点提供了4倍于传统网卡的带宽，更在网络阻塞时实现了无缝的负载均衡分配，彻底颠覆了大规模AI基础设施的弹性网络设计范式 29。

### **2.4 芯粒封装的逆向工程：Eliyan与标准基板的高效互联**

虽然先进封装（如CoWoS）主导了当前的AI芯片互联，但其成本和产能瓶颈始终是悬在行业头顶的达摩克利斯之剑。硅谷的初创企业Eliyan（已获得包括AMD、Arm、Meta及Samsung在内的5000万美元战略投资）通过其突破性的NuLink技术，展示了一条完全不同的技术路线 4。  
Eliyan的NuLink PHY技术旨在打破对昂贵硅中介层（Silicon Interposers）的依赖。通过高度优化的信号均衡与信道调制算法，NuLink使得芯片设计者能够在成本低廉、供应链成熟的标准有机封装基板（凸点间距100-130微米）上，实现与先进封装（40-55微米凸点间距）相媲美的Die-to-Die（D2D）互联带宽、极低延迟以及出色的功耗效率 33。其产品全面兼容UCIe与BoW等开放标准，单向数据链路速率已从64G跨越至224G，并正在研发448G的前沿标准 4。这种技术不仅降低了制造废料，还极大地增强了系统的可持续性，使得构建更大规模的同构及异构多裸片架构成为可能，彻底颠覆了AI算力芯片的成本结构 36。

### **2.5 冲破物理极限的终局形态：硅光与共封装光学 (CPO) 的爆发**

当铜线互联在功耗、发热与带宽距离上的物理限制逐渐见顶，整个产业界已经意识到，未来的数据中心互联必须走向光子化。在这一共识的推动下，光学互联初创企业迎来了疯狂的资本涌入。  
2026年3月，共封装光学（CPO）领军企业Ayar Labs宣布完成高达5亿美元的Series E轮融资（由Neuberger Berman领投），公司估值飙升至37.5亿美元 37。Ayar Labs研发的TeraPHY光学I/O芯粒，将光电转换模块直接与GPU等逻辑计算核心集成在同一个封装内。这种CPO架构能够提供高达8 Tbps的芯片级互联带宽，相比于最先进的铜互联技术，其带宽提升了5-10倍，功耗效率优化了4-8倍，延迟降低了10倍，成为了破解AI基础设施“功耗墙”的利器 39。  
Marvell对Celestial AI价值32.5亿美元的并购案同样印证了这一趋势 41。Celestial AI的Photonic Fabric（光子结构）技术平台突破了传统硅光器件必须放置在芯片边缘（Edge）的限制，允许光学元件在3D封装中与高功率XPU进行垂直共封装。这种卓越的热稳定性不仅缩短了信号路径，更释放了宝贵的硅片边缘面积（Beachfront），使得系统能够集成更多的HBM内存，从物理空间布局上彻底改变了芯片的内部组装范式 41。  
在更广泛的生态体系中，各类光学元件初创公司正在百花齐放（详见表1）。这些公司涵盖了从核心发光元件、光路切换到全光计算的每一个细分领域，标志着全光数据中心网络已从实验室步入大规模商业化前夕。

| 公司名称 | 核心光学互联技术与价值主张 | 市场角色与应用场景定位 |
| :---- | :---- | :---- |
| **Ayar Labs** | 开发TeraPHY光学I/O芯粒与多波长光源，提供比铜缆高5-10倍带宽的共封装光学（CPO）方案 42。 | AI节点间超高带宽互联，获5亿美元E轮融资，估值37.5亿美元 39。 |
| **Celestial AI** | Photonic Fabric光子结构，支持3D垂直共封装，无需占用硅片边缘面积，极大释放HBM集成空间 41。 | 被Marvell以32.5亿美元收购，主攻大规模多机架光互联与内存解构网络 41。 |
| **Avicena** | 利用GaN微型LED阵列替代高功耗激光器，通过高并发、低单路速率实现超低功耗的短距（10米内）光通信 42。 | 解决AI集群短距离连接中的极致功耗危机，引领新型光子架构标准的制定 42。 |
| **DustPhotonics** | 专注于低功耗、高速率的硅光集成电路（PICs），采用创新的低损耗激光耦合方法 42。 | 提供800G及1.6T DR PICs，直接赋能下一代可插拔光模块与CPO应用架构 42。 |
| **Akhetonics** | 研发全光通用处理器，将处理、接口及内存访问全部保持在光域内，通过光复用轻松扩展带宽并大幅降低能耗 42。 | 引领光子计算前沿，目标在大幅度减少电子组件的同时实现算力与能效的双重飞跃 42。 |
| **Lightium** | 致力于薄膜铌酸锂（TFLN）代工服务，TFLN是支持单通道200G甚至3.2Gbps以上速率的革命性非线性电光材料 42。 | 推动下一代超高速光调制的商业化，打破传统硅光和磷化铟材料的物理极限 42。 |

*表 1：AI驱动下的光互联与光学组件核心初创企业图谱*

## **三、 前沿互联标准与测试验证技术的演进范式**

在互联硬件层面的激烈角逐之外，底层的协议标准与测试验证方法论同样在经历着深刻的范式转移。理解这些标准的演进，不仅有助于把握技术脉络，更是寻找创业蓝海的关键先决条件。

### **3.1 开放Scale-up与Scale-out网络的突围战：UALink与UEC**

为了打破单一垄断企业在横向与纵向扩展网络上的封闭壁垒，由AMD、Intel、Broadcom及Marvell等巨头主导的超级互联联盟正加速推进开放标准的落地。  
在纵向扩展（Scale-up）领域，Ultra Accelerator Link (UALink) 联盟于2025年正式发布了UALink 1.0规范。该规范定义了单通道200G和128G的高带宽电学互联物理层，支持在单个AI计算Pod内直连多达1,024个加速器，并提供原生的Load/Store直接内存访问语义 10。紧随其后，预计于2026年Q2发布的UALink 2.0规范将是一次重大的架构升级，其核心在于引入了网络内计算（In-Network Compute, INC）功能 10。INC允许加速器之间直接进行计算和通信协同，从而在密集的机架环境中大幅减少不必要的数据搬运，提升分布式训练的带宽利用率。此外，UALink还同步发布了全面兼容UCIe 3.0规范的Chiplet集成标准，允许第三方开发者以极低的门槛将UALink接口集成至定制化SoC中 10。  
在横向扩展（Scale-out）领域，超以太网联盟（UEC）于2025年发布了UEC 1.0规范，并在2026年初更新至1.0.2版本 43。UEC旨在重构古老的以太网协议栈，使其完全适应AI与HPC的严苛要求。通过摒弃容易造成拥塞的传统TCP/IP拥塞控制算法，UEC引入了灵活的拥塞管理机制（如CMS算法的校正）、多路径并发喷射（Multipath Spraying）技术以及针对微小报文性能的极致优化 43。这些改进使得任何符合UEC标准的底层以太网交换芯片都能够提供接近无损网络（Lossless Network）的极致性能。

### **3.2 高速接口的测试与验证挑战：PCIe 7.0时代的“隐形屏障”**

随着PCIe 6.0（64 GT/s）与PCIe 7.0（128 GT/s）的相继确立，芯片验证与测试设备的复杂性呈现指数级爆炸。在如此高频率的PAM4调制下，信号变得极其微弱且眼图几乎完全闭合，必须强依赖于前向纠错（FEC）机制来保障数据的完整性 7。这一变化彻底颠覆了传统的物理层验证流程。  
硬件设计人员面临的最大障碍之一，是如何在128 GT/s的速率下可靠地验证接收器（Rx）的性能。传统的眼图压力测试和手动干扰注入在此速率下已完全失效。针对这一行业痛点，是德科技（Keysight）、泰克（Tektronix）和Viavi等测试设备巨头在2026年的PCI-SIG开发者大会上密集发布了革命性的解决方案 8。 例如，Keysight推出了专用的N5991PB7A接收器测试自动化软件。该中间件通过API与底层的M8050A BERT模式发生器联动，能够在无需人工干预的情况下，自动对TP3和TP2接收器压力信号进行微秒级的精准校准，并实时输出一致性校准报告 8。这一自动化流程能够在其引发不可逆的流片失败前，提前暴露芯片接收器的物理弱点。同时，Viavi推出了Xgig PCIe 7.0协议分析平台，该平台不仅提供针对PCIe、CXL及NVMe的全栈协议解码，还创新性地引入了链路训练和状态状态机（LTSSM）强制覆盖测试与模块化探测插入器（Interposer），消除了传统测试线缆自身对高速信号完整性的破坏 46。这些测试验证技术的进步，构成了支撑整个AI互联生态不断攀登速率高峰的隐形基石。

## **四、 高潜力的创业与深度研究方向探讨**

基于前文对宏观痛点、行业标杆解法、先进芯片架构以及前沿通信标准的详尽研究，针对“AI基础设施接口互联”这一高度技术密集的领域，本报告提炼并设计了五个具备深厚学术研究价值与极高商业变现潜力的深度创业方向。

### **创业方向一：基于CXL原生语义的大模型推理存储中间件系统**

**【行业背景与痛点逻辑】** 尽管基于CXL协议的硬件基础设施（如Astera Labs的Leo内存控制器和Marvell的混合交换机）已逐步成熟并实现量产，但要在生产环境中真正实现跨机架级别的大规模内存池化，上层软件中间件的缺失是当前最大的商业化阻碍。现有的Linux内核与分布式系统调度器并未针对CXL引入的不均匀内存访问（NUMA）架构进行极致优化。传统基于RDMA的内存解耦方案存在多级通信开销、复杂的握手协议以及严重的同步延迟，导致大语言模型（LLM）的KVCache在跨节点调用时效率极低，严重拖累了推理的并发吞吐量 3。  
**【技术路线与创业切入点】**

1. **弹性内存自动分配服务（Elastic Memory Services）：** 研发类似MemVerge Elastic Memory的进阶版中间件 19。该系统需要深入操作系统内核层，实时监控各类AI容器的内存使用热力图和缺页中断（Page Fault）频率。当预测到本地高带宽内存或主存即将枯竭时，通过亚毫秒级的CXL驱动自动映射远程内存池，从而从根本上消除Out-Of-Memory (OOM) 崩溃，解决数据中心普遍存在的“内存搁浅”（Stranded Memory）与资源利用率低下的顽疾。  
2. **针对LLM优化的原生KVCache对象存储底座：** 参考并商业化最新的学术研究成果（如Beluga架构）3。创业团队可开发直接建立在CXL互联架构之上的分布式KVCache管理系统。该系统利用CXL内存原生支持的Load/Store语义，使GPU能够直接寻址并读写远程共享内存池中的KVCache，完全旁路掉CPU干预以及RDMA的协议栈开销。通过在vLLM等主流推理框架底部重构通信库，预期可将“首Token生成时间”（TTFT）降低80%以上，极具技术壁垒与被头部云厂商收购的价值 3。  
3. **零IO（Zero-IO）共享内存通信引擎：** 在分布式异构计算（如基于Ray的架构）中，开发直接映射在CXL内存空间中的分布式张量（Tensor）管理器。这能实现计算节点间的零数据拷贝同步，彻底消除传统网络序列化与反序列化的时间成本 19。

### **创业方向二：摆脱先进封装依赖的高带宽Die-to-Die（D2D）互联IP核心**

**【行业背景与痛点逻辑】** 当前最高性能的AI加速器普遍采用台积电的CoWoS等2.5D/3D先进封装技术。然而，先进封装不仅成本极其高昂，其漫长的制造周期与产能瓶颈严重制约了AI芯片公司的出货速度 2。如果初创企业能够在极低成本、供应链高度成熟的标准有机封装基板（Organic Substrates，凸点间距100-130微米）上，实现与硅中介层先进封装相媲美的D2D互联带宽，将彻底颠覆现有的半导体制造成本结构。  
**【技术路线与创业切入点】**

1. **高性能、低功耗的标准封装PHY IP：** 深度对标Eliyan公司的NuLink互联技术 33。通过研发高级的混合信号信道均衡技术、先进的前向纠错算法以及创新的多级信令调制（如将64G PAM4提升至224G甚至448G），使标准有机基板上的芯片互联能够在功耗与信号完整性上媲美先进封装 4。该IP必须完全兼容UCIe 3.0与BoW等行业开放标准，从而为系统架构师提供即插即用的模块化组件 33。  
2. **异构Chiplet的协议适配与内网硬件级安全网关：** 随着Chiplet技术的普及，未来的单颗AI芯片内部将混合组装来自Intel、NVIDIA或第三方初创公司的各种芯粒 5。这种“大杂烩”式的物理集成带来了极其严峻的硬件安全风险（例如某一颗非受信芯粒可能被植入硬件木马以窥探全局显存）。创业团队可基于UCIe 3.0标准引入的UDA（UCIe DFx Architecture），开发针对Chiplet内网的实时硬件级防火墙及合规性自动化测试IP模块，监控D2D链路上的异常指令流，该领域的空白具有极高的商业授权（IP Licensing）价值 5。

### **创业方向三：融合多协议与网络内计算（In-Network Compute）的智能超级网卡**

**【行业背景与痛点逻辑】** 随着云数据中心加速向多机架、跨节点部署演进，单一的网络架构已经无法适应需求。AI计算集群不仅需要处理海量数据的横向以太网摄入（Scale-out），还需要维持加速器之间缓存一致性的纵向互联（UALink），同时还依赖CXL架构进行主存解构 25。现有的通用网卡或专有网络接口芯片在应对多源异构协议时往往成为系统瓶颈，难以支撑高并发的大规模并行计算。  
**【技术路线与创业切入点】**

1. **多协议自适应混合Fabric网卡与交换引擎：** 汲取XConn（以5.4亿美元被Marvell收购）成功打造Apollo混合交换芯片的经验，致力于在一块硅片上同时原生支持以太网（UEC标准）、PCIe 6.0/7.0、CXL 3.1以及即将到来的UALink 1.0/2.0流量的路由与交换 26。通过硬件级别的深度融合，极大降低系统主板的布线复杂度和网络跳数（Hops），为构建无缝的高密度智算集群提供核心部件。  
2. **弹性AI内存与通信融合中间件网卡（SuperNIC）：** 瞄准类似Enfabrica（完成1.15亿美元C轮融资，推出3.2Tbps ACF-S芯片）的产品形态 28。开发能够提供多端口800G超以太网连接、支持定制化传输层协议，并能在网卡（NIC）层面直接通过硬件电路卸载分布式AI集合通信（如AllReduce、AllGather、ReduceScatter）任务的智能网卡。尤其需要突破多路径容错与动态流量并发喷射（Multipath Spraying）技术，确保在网络局部拥塞时能够自动重路由数据包，大幅度降低跨节点GPU通信的尾随延迟（Tail Latency），构建极具弹性的AI计算网络 29。

### **创业方向四：冲破铜互联物理极限的硅光与CPO核心组件开发**

**【行业背景与痛点逻辑】** 虽然Astera Labs的重定时器等电学方案暂时延缓了铜线互联的生命周期，但在迈向1.6T乃至3.2T单端口速率的道路上，铜缆在功耗、发热、抗干扰以及传输距离上的物理限制已经显现出不可逾越的鸿沟。全光网络（All-Optical Networks）是解决数据中心“通信墙”的终极技术范式。然而，硅光产业涉及极其复杂的非线性光学材料、微纳级制造工艺与高精度对准封装。科技巨头（如Marvell收购Celestial AI）更倾向于直接并购成熟的系统级集成方案公司，这为在底层细分发光、调制与计算组件上取得单点技术突破的初创团队留下了广阔的发展空间 41。  
**【技术路线与创业切入点】**

1. **新型光电调制材料的产业化破局（如薄膜铌酸锂 TFLN）：** 传统的硅光或磷化铟（InP）材料在面对单通道200G甚至更高的数据速率时，其电光调制带宽与插入损耗已逼近物理极限。薄膜铌酸锂（TFLN）因其极高的电光系数、超宽的调制带宽与极低的信号损耗特性，被业界公认为是支撑2028年以后3.2Tbps节点的核心非线性光学材料。针对TFLN调制器设计及其在标准晶圆厂中的良率提升与代工服务（如Lightium的技术路径）进行工艺攻坚，是当前硬件科技创业的深水区与高回报区 42。  
2. **极低功耗的短距互联微型LED（MicroLED）阵列：** 在极短距离（如10米以内）的AI服务器内部机架连线中，使用标准高速激光器虽然能满足带宽，但其绝对功耗过高，不够经济。类似于Avicena公司的创新路线，可以研发基于氮化镓（GaN）的微型LED阵列技术。相比于驱动少量高速激光器，该方案利用超大规模的低速并行光通道阵列，以极低的系统能耗实现Tbps级别的聚合带宽，是取代服务器内部高速铜线与重定时器极具潜力的新型光学物理架构 42。  
3. **全光计算处理器与纯光网络矩阵切换（OCS）：** 摒弃传统“光-电-光”转换所带来的高昂延迟与能耗惩罚，研发直接在光域内执行通用逻辑处理或专门针对大模型注意力机制的矩阵乘法运算硬件系统（如Akhetonics、Lightmatter、Lightsolver的方案）42。此外，结合MEMS（微机电系统）技术开发纯光路切换矩阵，支持数据中心资源的纳秒级动态拓扑重构，实现从光通信向光计算的跨越式发展 42。

### **创业方向五：面向PCIe 6.0/7.0与CXL的AI驱动协议分析与自动化验证系统**

**【行业背景与痛点逻辑】** 每次底层通信协议的升级换代，都伴随着测试验证工程的噩梦。在128 GT/s的PCIe 7.0速率下，眼图完全闭合是常态，前向纠错（FEC）机制的介入使得数据流的物理层验证和协议层解码变得异常困难 7。传统的硬件工程师依靠手动调整示波器探头、人工分析信噪比畸变与注入压力的时代已经一去不复返。芯片流片前后的合规性测试如果不够严谨，将导致巨额的资金损失。  
**【技术路线与创业切入点】**

1. **基于AI驱动的一体化自动化校准与验证中间件：** 虽然像安立（Anritsu）和泰克（Tektronix）这样的传统设备巨头垄断了示波器和BERT发生器等底层精密测量硬件，但在专用的上层协议一致性测试、链路训练自动化以及FEC纠错压力边界探测等算法层，依然存在巨大的软件空白 7。初创企业可以开发能够通过标准API控制所有底层仪器的AI测试中间件平台。该软件系统可以利用机器学习算法自动寻优复杂的均衡器（EQ）设置，预测接收器（Rx）在不同温度、电压漂移下的脆弱点，并全自动执行TP2/TP3校准测试，一键生成符合PCI-SIG标准的合规性报告，从而大幅削减芯片原厂的开发时间 8。  
2. **超低损耗模块化插入器（Interposers）与全链路数字孪生EDA工具：** 传统的测试线缆自身就是劣化高频信号的罪魁祸首。研发物理层面的无源或有源超低损耗探测插入器，以便在不破坏原有链路阻抗特性的情况下无损捕获微弱信号 46。同时，开发能够精确模拟实际复杂AI主板布线、过孔分布及连接器阻抗特性的信道仿真EDA（电子设计自动化）数字孪生工具，帮助芯片设计团队在早期阶段通过纯软件数字仿真准确识别眼图闭合风险，防患于未然。

## **五、 结论**

综上所述，当前AI基础设施所面临的核心困境，本质上是一场由生成式大语言模型算力狂飙引发的系统级“木桶效应”。当CPU与GPU的绝对计算能力不再是短板时，底层互联接口的信号完整性坍塌、网络协议的路由开销、物理封装的热密度极限以及内存扩展的物理隔离，共同铸就了阻碍AI应用进一步规模化的“互联墙”与“内存墙”。  
通过对Astera Labs、Marvell、Ayar Labs、Eliyan以及Enfabrica等行业领军企业的深度解构，我们不难发现，未来的底层硬件互联架构正不可逆转地向**高度解耦化、动态池化、开放标准化以及光子化**方向演进。  
从短中期的工程落地来看，基于复杂DSP算法的重定时器、智能有源线缆（如Astera Labs的Aries与Taurus）以及多协议兼容的混合交换芯片（兼容PCIe 6/7与CXL 3.x）的电学解决方案，结合强大的内存调度与KVCache优化软件中间件（如MemVerge的Elastic Memory与Beluga架构），是解决当前数据中心互联瓶颈最为务实且最具变现能力的商业路线。  
而从中长期的产业终局来看，以薄膜铌酸锂、微型LED及共封装光学（CPO）为代表的光电融合生态，辅以彻底打破单一厂商锁定、完全开放互操作的UALink与超以太网联盟（UEC）网络架构标准，将成为打破人类半导体物理极限的最终出路。  
对于科研工作者与科技创业者而言，硬件侧的技术突破口深深扎根于标准封装下的高性能Die-to-Die互联IP、硅光材料学突破及多协议融合网卡的设计创新中；而软件侧的最大红利，则潜藏于针对CXL内存池化及大模型推理底层的分布式共享内存调度系统之中。在这一资本密集且技术壁垒极高的AI基础设施赛道上，谁能准确把握上述核心痛点，并提供在工程上具备高度可靠性、在成本上具备极强竞争力的模块化破局方案，谁就真正掌握了通向下一代计算纪元的核心钥匙。

#### **Works cited**

1. AI and Memory Wall \- arXiv, accessed May 22, 2026, [https://arxiv.org/html/2403.14123v1](https://arxiv.org/html/2403.14123v1)  
2. Marvell's $540M XConn Acquisition Signals AI Interconnect | Introl Blog, accessed May 22, 2026, [https://introl.com/blog/marvell-xconn-acquisition-cxl-ualink-infrastructure-2026](https://introl.com/blog/marvell-xconn-acquisition-cxl-ualink-infrastructure-2026)  
3. Beluga: A CXL-Based Memory Architecture for Scalable and Efficient LLM KVCache Management \- arXiv, accessed May 22, 2026, [https://arxiv.org/html/2511.20172v2](https://arxiv.org/html/2511.20172v2)  
4. Eliyan: $50 Million Raised To Scale AI Interconnect Chiplets, accessed May 22, 2026, [https://pulse2.com/eliyan-50-million-funding/](https://pulse2.com/eliyan-50-million-funding/)  
5. The Chiplet Revolution: How Advanced Packaging and UCIe are ..., accessed May 22, 2026, [https://www.design-reuse.com/news/202529865-the-chiplet-revolution-how-advanced-packaging-and-ucie-are-redefining-ai-hardware-in-2025/](https://www.design-reuse.com/news/202529865-the-chiplet-revolution-how-advanced-packaging-and-ucie-are-redefining-ai-hardware-in-2025/)  
6. Aries PCIe®/CXL® Smart DSP Retimers \- ASTERA LABS, INC., accessed May 22, 2026, [https://www.asteralabs.com/products/pcie-cxl-smart-dsp-retimers/](https://www.asteralabs.com/products/pcie-cxl-smart-dsp-retimers/)  
7. PCIe Test and Validation Solutions \- Tektronix, accessed May 22, 2026, [https://www.tek.com/en/solutions/application/high-speed-serial-communication/pcie](https://www.tek.com/en/solutions/application/high-speed-serial-communication/pcie)  
8. PCIe 7.0 Roundup: Test and Timing Tools Emerge as Ecosystem Takes Shape \- News, accessed May 22, 2026, [https://www.allaboutcircuits.com/news/pcie-7.0-roundup-test-and-timing-tools-emerge-as-ecosystem-takes-shape/](https://www.allaboutcircuits.com/news/pcie-7.0-roundup-test-and-timing-tools-emerge-as-ecosystem-takes-shape/)  
9. The Long & Short of AI: Building Scalable Data Centers in the PCIe ..., accessed May 22, 2026, [https://www.asteralabs.com/the-long-and-short-of-ai-building-scalable-data-centers-in-the-pcie-6-x-era/](https://www.asteralabs.com/the-long-and-short-of-ai-building-scalable-data-centers-in-the-pcie-6-x-era/)  
10. UALink Roadmap Insights: Accelerating Open, Scalable AI Networking, accessed May 22, 2026, [https://ualinkconsortium.org/blog/ualink-roadmap-insights-accelerating-open-scalable-ai-networking-1296/](https://ualinkconsortium.org/blog/ualink-roadmap-insights-accelerating-open-scalable-ai-networking-1296/)  
11. Scorpio Smart Fabric Switch \- ASTERA LABS, INC., accessed May 22, 2026, [https://www.asteralabs.com/products/scorpio-smart-fabric-switch/](https://www.asteralabs.com/products/scorpio-smart-fabric-switch/)  
12. Aries PCIe®/CXL® Smart Cable Modules \- ASTERA LABS, INC., accessed May 22, 2026, [https://www.asteralabs.com/products/aries-smart-cable-modules/](https://www.asteralabs.com/products/aries-smart-cable-modules/)  
13. Taurus Smart Cable Module Product Brief \- Astera Labs, accessed May 22, 2026, [https://www.asteralabs.com/wp-content/uploads/2021/03/Taurus-Smart-Cable-Module-Product-Brief.pdf](https://www.asteralabs.com/wp-content/uploads/2021/03/Taurus-Smart-Cable-Module-Product-Brief.pdf)  
14. Taurus Smart Cable Modules™: An Active \+ Smart Approach to 200/400/800GbE, accessed May 22, 2026, [https://www.asteralabs.com/taurus-smart-cable-module-smart-approach-to-200-400-800-gbe/](https://www.asteralabs.com/taurus-smart-cable-module-smart-approach-to-200-400-800-gbe/)  
15. Aries Product Requirements Specification \- Astera Labs, accessed May 22, 2026, [https://www.asteralabs.com/wp-content/uploads/2021/11/Astera\_Labs\_Blog-Taurus\_Smart\_Cable\_Modules.pdf](https://www.asteralabs.com/wp-content/uploads/2021/11/Astera_Labs_Blog-Taurus_Smart_Cable_Modules.pdf)  
16. Taurus Ethernet Smart Cable Modules™ \- OIF Forum, accessed May 22, 2026, [https://www.oiforum.com/wp-content/uploads/OIF\_PLL\_Demo\_AsteraLabs\_OFC2023.pdf](https://www.oiforum.com/wp-content/uploads/OIF_PLL_Demo_AsteraLabs_OFC2023.pdf)  
17. Leo CXL® Smart Memory Controllers \- ASTERA LABS, INC., accessed May 22, 2026, [https://www.asteralabs.com/products/leo-cxl-smart-memory-controllers/](https://www.asteralabs.com/products/leo-cxl-smart-memory-controllers/)  
18. Astera Labs' Leo CXL Smart Memory Controllers on Microsoft Azure M-series Virtual Machines Overcome the Memory Wall, accessed May 22, 2026, [https://www.asteralabs.com/news/astera-labs-leo-cxl-smart-memory-controllers-on-microsoft-azure-m-series-virtual-machines-overcome-the-memory-wall/](https://www.asteralabs.com/news/astera-labs-leo-cxl-smart-memory-controllers-on-microsoft-azure-m-series-virtual-machines-overcome-the-memory-wall/)  
19. CXL Technology Deep Dive \- MemVerge, accessed May 22, 2026, [https://memverge.com/cxl-technology/](https://memverge.com/cxl-technology/)  
20. Elastic Memory | MemVerge, accessed May 22, 2026, [https://memverge.com/wp-content/uploads/MemVerge-Elastic-Memory\_CXL-Forum-FMS-2023.pdf](https://memverge.com/wp-content/uploads/MemVerge-Elastic-Memory_CXL-Forum-FMS-2023.pdf)  
21. MemVerge and SK hynix Announce Endless Memory \- PR Newswire, accessed May 22, 2026, [https://www.prnewswire.com/news-releases/memverge-and-sk-hynix-announce-endless-memory-301829977.html](https://www.prnewswire.com/news-releases/memverge-and-sk-hynix-announce-endless-memory-301829977.html)  
22. Beluga: A CXL-Based Memory Architecture for Scalable and Efficient LLM KVCache Management \- ResearchGate, accessed May 22, 2026, [https://www.researchgate.net/publication/397983834\_Beluga\_A\_CXL-Based\_Memory\_Architecture\_for\_Scalable\_and\_Efficient\_LLM\_KVCache\_Management](https://www.researchgate.net/publication/397983834_Beluga_A_CXL-Based_Memory_Architecture_for_Scalable_and_Efficient_LLM_KVCache_Management)  
23. Beluga: A CXL-Based Memory Architecture for Scalable and Efficient LLM KVCache Management | Cool Papers, accessed May 22, 2026, [https://papers.cool/arxiv/2511.20172v2](https://papers.cool/arxiv/2511.20172v2)  
24. \[2511.20172\] Beluga: A CXL-Based Memory Architecture for Scalable and Efficient LLM KVCache Management \- arXiv, accessed May 22, 2026, [https://arxiv.org/abs/2511.20172](https://arxiv.org/abs/2511.20172)  
25. Marvell to Acquire XConn Technologies, Expanding Leadership in AI Data Center Connectivity, accessed May 22, 2026, [https://www.marvell.com/company/newsroom/marvell-to-acquire-xconn-technologies-expanding-leadership-in-ai-data-center-connectivity.html](https://www.marvell.com/company/newsroom/marvell-to-acquire-xconn-technologies-expanding-leadership-in-ai-data-center-connectivity.html)  
26. XConn Buy Unveils Marvell's AI Connectivity Imperative \- EE Times, accessed May 22, 2026, [https://www.eetimes.com/xconn-buy-unveils-marvells-ai-connectivity-imperative/](https://www.eetimes.com/xconn-buy-unveils-marvells-ai-connectivity-imperative/)  
27. Marvell's XConn Buy Yields a Two-Pronged Open Fabric Play Against NVLink, accessed May 22, 2026, [https://futurumgroup.com/insights/marvells-xconn-buy-yields-a-two-pronged-open-fabric-play-against-nvlink/](https://futurumgroup.com/insights/marvells-xconn-buy-yields-a-two-pronged-open-fabric-play-against-nvlink/)  
28. Enfabrica Raises $115M in New Funding to Advance its Leadership ..., accessed May 22, 2026, [https://www.iagcapitalpartners.com/news/enfabrica-115m-series-c](https://www.iagcapitalpartners.com/news/enfabrica-115m-series-c)  
29. Enfabrica, accessed May 22, 2026, [https://enfabrica.net/](https://enfabrica.net/)  
30. Press Release: Enfabrica Raises $125 Million Series B to Fuel Ramp of AI Infrastructure Networking Chips | by Sander Arts, accessed May 22, 2026, [https://blog.enfabrica.net/press-release-enfabrica-raises-125-million-series-b-to-fuel-ramp-of-ai-infrastructure-networking-a8a0b21653d2](https://blog.enfabrica.net/press-release-enfabrica-raises-125-million-series-b-to-fuel-ramp-of-ai-infrastructure-networking-a8a0b21653d2)  
31. CEO Blog: Enfabrica's ACF-S Millennium Chip Launch, Series C Funding, and More, accessed May 22, 2026, [https://blog.enfabrica.net/ceo-blog-enfabricas-acf-s-millennium-chip-launch-series-c-funding-and-more-94e36eafaafb](https://blog.enfabrica.net/ceo-blog-enfabricas-acf-s-millennium-chip-launch-series-c-funding-and-more-94e36eafaafb)  
32. Eliyan Secures $50 Million in Strategic Investments from Leading Hyperscalers and AI Infrastructure Providers to Accelerate Scalable AI Systems, accessed May 22, 2026, [https://eliyan.com/press-release/eliyan-secures-50-million-in-strategic-investments/](https://eliyan.com/press-release/eliyan-secures-50-million-in-strategic-investments/)  
33. Technology \- Eliyan, accessed May 22, 2026, [https://eliyan.com/technology/](https://eliyan.com/technology/)  
34. Products \- Eliyan, accessed May 22, 2026, [https://eliyan.com/Products/](https://eliyan.com/Products/)  
35. About \- Eliyan, accessed May 22, 2026, [https://eliyan.com/about/](https://eliyan.com/about/)  
36. Eliyan Sets New Standard for Chiplet Interconnect Performance with Latest PHY Delivering Data Rate of 64Gbps on 3nm Process Using Standard Packaging, accessed May 22, 2026, [https://eliyan.com/press-release/eliyan-sets-new-standard-for-chiplet-interconnect-performance/](https://eliyan.com/press-release/eliyan-sets-new-standard-for-chiplet-interconnect-performance/)  
37. Ayar Labs Raises US$500 Million \- Optics & Photonics News, accessed May 22, 2026, [https://www.optica-opn.org/home/industry/2026/march/ayar\_labs\_raises\_us$500\_million/](https://www.optica-opn.org/home/industry/2026/march/ayar_labs_raises_us$500_million/)  
38. Ayar Labs Revenue 2025: $91.6M ARR, $1B Valuation \- GetLatka, accessed May 22, 2026, [https://getlatka.com/companies/ayar-labs-](https://getlatka.com/companies/ayar-labs-)  
39. Ayar Labs Closes $500M Series E, Accelerates Volume Production of Co‑Packaged Optics, accessed May 22, 2026, [https://ayarlabs.com/news/ayar-labs-closes-500m-series-e-accelerates-volume-production-of-co-packaged-optics/](https://ayarlabs.com/news/ayar-labs-closes-500m-series-e-accelerates-volume-production-of-co-packaged-optics/)  
40. Ayar Labs Raises $500M Series E for Co-Packaged Optics \- TAMradar Funding Rounds Signals, accessed May 22, 2026, [https://www.tamradar.com/funding-rounds/ayar-labs-series-e-500m](https://www.tamradar.com/funding-rounds/ayar-labs-series-e-500m)  
41. Marvell to Acquire Celestial AI, Accelerating Scale-up Connectivity ..., accessed May 22, 2026, [https://investor.marvell.com/news-events/press-releases/detail/1000/marvell-to-acquire-celestial-ai-accelerating-scale-up-connectivity-for-next-generation-data-centers](https://investor.marvell.com/news-events/press-releases/detail/1000/marvell-to-acquire-celestial-ai-accelerating-scale-up-connectivity-for-next-generation-data-centers)  
42. Optical Component Startup Tracker \- Cignal AI, accessed May 22, 2026, [https://cignal.ai/2025/11/optical-component-startup-tracker/](https://cignal.ai/2025/11/optical-component-startup-tracker/)  
43. Release Notes \- Ultra Ethernet Consortium, accessed May 22, 2026, [https://ultraethernet.org/wp-content/uploads/sites/20/2026/01/UE-Specification-1.0.2-release-notes.pdf](https://ultraethernet.org/wp-content/uploads/sites/20/2026/01/UE-Specification-1.0.2-release-notes.pdf)  
44. UEC 2025 in Review: Preparing for What Comes Next \- A Letter from UEC's Chair, accessed May 22, 2026, [https://ultraethernet.org/uec-2025-in-review-preparing-for-what-comes-next-a-letter-from-uecs-chair/](https://ultraethernet.org/uec-2025-in-review-preparing-for-what-comes-next-a-letter-from-uecs-chair/)  
45. Ultra Ethernet Consortium (UEC) Launches Specification 1.0 Transforming Ethernet for AI and HPC at Scale, accessed May 22, 2026, [https://ultraethernet.org/ultra-ethernet-consortium-uec-launches-specification-1-0-transforming-ethernet-for-ai-and-hpc-at-scale/](https://ultraethernet.org/ultra-ethernet-consortium-uec-launches-specification-1-0-transforming-ethernet-for-ai-and-hpc-at-scale/)  
46. Illuminate High-Speed PCIe Lanes with Protocol Analyzers | Keysight Blogs, accessed May 22, 2026, [https://www.keysight.com/blogs/en/tech/educ/protocol-analyzer](https://www.keysight.com/blogs/en/tech/educ/protocol-analyzer)  
47. VIAVI Announces Investment in PCIe 7.0 Protocol Analysis Testing Platform, accessed May 22, 2026, [https://www.viavisolutions.com/en-us/news-releases/viavi-announces-investment-pcie-70-protocol-analysis-testing-platform](https://www.viavisolutions.com/en-us/news-releases/viavi-announces-investment-pcie-70-protocol-analysis-testing-platform)  
48. Anritsu to Exhibit Cutting-Edge PCI-Express® 6.0 and 7.0 Signal Integrity Solutions at DesignCon 2025, accessed May 22, 2026, [https://www.anritsu.com/en-us/test-measurement/news/news-releases/2025/2025-01-27-us01](https://www.anritsu.com/en-us/test-measurement/news/news-releases/2025/2025-01-27-us01)