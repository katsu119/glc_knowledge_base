 clc;
clear;
fs = 16*10^9;   %采样频率16GHz
T = 1/fs;       %采样间隔
fin1 = 809/8192*fs; %输入正弦波频率
Tin = 1/(fin1);     %输入正弦波间隔 

N = 2^24;                    %采样点数
M = 16;                      %采样通道：16
t = 0:1/fs:(N-1)/fs;         %采样时刻

%%  generate random mismatch variable
skew_mismatch = zeros(1,M);
gain_mismatch = ones(1,M);
offset_mismatch = zeros(1,M);
for i = 1:M     %generate random mismatch variable for each channel
    skew_mismatch(i) = randn(1,1) * 0.01*T*8;
    %gain_mismatch(i) = 1+randn(1,1) * 0.01;
    %offset_mismatch(i) = randn(1,1) * 0.01;
end
%skew_mismatch=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
offset_mismatch=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
gain_mismatch=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1];
%gain_mismatch=[0.991887503020774,1.01300148465590,0.994576539575034,0.996336265137245,0.981216938204290,1.00496433047322,0.995051238568253,1.01192478195326,0.994329693357975,1.00282349589059,1.01534902874259,0.994490723528908,0.995716693376054,0.987881100025152,1.01287431110972,0.991022806984492];
%40mv_offset
%offset_mismatch=[-0.0225884686100365,-0.0130768829630527,0.0357839693972576,0.0303492346633185,0.00714742903826096,0.0148969760778546,0.00671497133608081,0.0163023528916473,0.00726885133383238,-0.00787282803758638,-0.0106887045816803,0.0143838029281510,0.0137029854009523,-0.00241447041607358,-0.00864879917324457,0.00627707287528727];
%20mv_offset
%offset_mismatch=[0.00216855990585554,-0.0129542156382229,0.00200255861354737,0.00748091512289529,0.0152633943160118,-0.0136529392958583,0.00576532659383278,-0.00822004313859303,-0.00248219450326367,-0.00277537739812483,-0.0071452634256301,0.000369503804489841,-0.00267406198087474,0.000453181831691423,0.0102554853904953,-0.0177135464092140];

%% Before CAL
Vi=zeros(N,1);
Ao_nocal=zeros(N,1);
D1_nocal=zeros(N,8);
D2_nocal=zeros(N,6);
for i = 1:N
    if(mod(i,M) == 0)
        Vi(i) = gain_mismatch(M) * 0.78 * cos(2*pi*fin1*(T*(i-1) + skew_mismatch(M))) + offset_mismatch(M);
    else
        Vi(i) = gain_mismatch(mod(i,M)) * 0.78 * cos(2*pi*fin1*(T*(i-1) + skew_mismatch(mod(i,M)))) + offset_mismatch(mod(i,M));
    end
end
[Ao_nocal,D1_nocal,D2_nocal]=ADC(Vi,N); 

[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Ao_nocal),fs,8192,"校准前");
hold on

%% Timing Skew Calibration
%cycle = 4096;   %用于迭代的数据个数
CN = 1000000;     	%迭代次数
u = 2^-70; %2^-37;      %迭代步长
delta_adjust = zeros(M,CN);
error = zeros(M,CN);

for i=1:M
	Sub_ADC_all(i,:) =Ao_nocal(i:M:end,1);
end

for i=1:CN
    delta_adjust(1,i+1) = delta_adjust(1,i) - u * error(1,i);
    delta_adjust(2,i+1) = delta_adjust(2,i) - u * error(2,i);
    delta_adjust(3,i+1) = delta_adjust(3,i) - u * error(3,i);
    delta_adjust(4,i+1) = delta_adjust(4,i) - u * error(4,i);
    delta_adjust(5,i+1) = delta_adjust(5,i) - u * error(5,i);
    delta_adjust(6,i+1) = delta_adjust(6,i) - u * error(6,i);
    delta_adjust(7,i+1) = delta_adjust(7,i) - u * error(7,i);
    delta_adjust(8,i+1) = delta_adjust(8,i) - u * error(8,i);
    delta_adjust(9,i+1) = delta_adjust(9,i) - u * error(9,i);
    delta_adjust(10,i+1) = delta_adjust(10,i) - u * error(10,i);
    delta_adjust(11,i+1) = delta_adjust(11,i) - u * error(11,i);
    delta_adjust(12,i+1) = delta_adjust(12,i) - u * error(12,i);
    delta_adjust(13,i+1) = delta_adjust(13,i) - u * error(13,i);
    delta_adjust(14,i+1) = delta_adjust(14,i) - u * error(14,i);
    delta_adjust(15,i+1) = delta_adjust(15,i) - u * error(15,i);
    delta_adjust(16,i+1) = delta_adjust(16,i) - u * error(16,i);
    
    for j=1:M+1
        if (mod(j,M)==1)
            Data_update(j) = 0.78*cos(2*pi*fin1*((j+i*M-1)*T+skew_mismatch(1)));
        elseif (mod(j,M)==0)
            Data_update(j) = 0.78*cos(2*pi*fin1*((j+i*M-1)*T+skew_mismatch(M)-delta_adjust(M,i+1)));
        else
            Data_update(j) = 0.78*cos(2*pi*fin1*((j+i*M-1)*T+skew_mismatch(mod(j,M))-delta_adjust(mod(j,M),i+1)));
        end
    end
    
    [Ao_update,D1_update,D2_update]=ADC(rot90(Data_update,-1),M+1);    %加-1是为了让矩阵顺时针旋转
 
    for k = 1:M
        Sub_ADC(k,:) = Ao_update(k:M:M+1);     %第一次放两个数，第二次之后就是把对应位置的数重复放两遍
    end
    
    %相邻通道做相关
    for k=1:M
        if k<M
        	I(k,:) = Sub_ADC(k,1:length(Sub_ADC(1,:))-1).*Sub_ADC(k+1,1:length(Sub_ADC(1,:))-1);
            Avg_I(k,i) = mean(I(k,:));	           
        else
            I(k,:) = Sub_ADC(k,1:length(Sub_ADC(1,:))-1).*Sub_ADC(1,2:length(Sub_ADC(1,:)));
            Avg_I(k,i) = mean(I(k,:));

        end
    end
    %计算误差平均值
    s=sum(Avg_I(:,i));
    avg=s/16;
    %将每个通道的相关值与平均值比较（假设通道1为理想）
    if i>1
        for k=1:M
            error(k+1,i+1) = Avg_I(k,i)-avg;
        end
    end
end
figure()
for i=1:M
    plot(skew_mismatch(i)-delta_adjust(i,1:CN))
    hold on
end

%% After All CAL
V_allcal = zeros(N,1);
Ao_allcal = zeros(N,1);


for i=1:N
   if (mod(i,M)==0)
       V_allcal(i) = 0.78 * cos(2*pi*fin1*((i-1)*T+skew_mismatch(mod(i,M)+M)-delta_adjust(mod(i,M)+M,CN)));
   elseif(mod(i,M)==1)
       V_allcal(i) =  0.78 * cos(2*pi*fin1*((i-1)*T+skew_mismatch(mod(i,M))));
   else
       V_allcal(i) =  0.78 * cos(2*pi*fin1*((i-1)*T+skew_mismatch(mod(i,M))-delta_adjust(mod(i,M),CN)));
   end
end

[Ao_allcal,D1_allcal,D2_allcal]=ADC(V_allcal,N); 

[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(Ao_allcal,fs,8192,"时钟失配失配校准后");