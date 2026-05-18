clc;
clear;
fs = 64*10^9;   %采样频率16GHz
T = 1/fs;       %采样间隔
fin1 = 809/8192*fs; %输入正弦波频率
Tin = 1/(fin1);     %输入正弦波间隔 

N = 2^24;                    %采样点数
M = 64;                      %采样通道：16
t = 0:1/fs:(N-1)/fs;         %采样时刻

%%  generate random mismatch variable
skew_mismatch = zeros(1,M);
gain_mismatch = ones(1,M);
offset_mismatch = zeros(1,M);
for i = 1:4     %generate random mismatch variable for each channel
    skew_mismatch(i) = randn(1,1) * 0.01*T*8;
    %gain_mismatch(i) = 1+randn(1,1) * 0.01;
    %offset_mismatch(i) = randn(1,1) * 0.01;
end
skew_mismatch=[600*10^-15,-400*10^-15,300*10^-15,-300*10^-15];

Vi=zeros(N/64,64);
Ao=zeros(N/64,64);
Ao_64=zeros(N/64,1);
mismatch=zeros(N/64-1,4);
mismatch_1=zeros(N/64-1,4);
e=zeros(N/64-1,4);
u=2^9;
%s=8;       %控制自相关后截尾的大小
s=1;
h=1;     %对sum没有截尾


step_size=1*10^-14;
Vi_1=zeros(N,1);


for i=1:N/64-1
    for t=1:64
        
    if(mod(t,4) == 0)
        Vi(i,t) =  0.8 * cos(2*pi*fin1*(T*((i-1)*64+t) + skew_mismatch(4)-mismatch_1(i,4)*step_size)) ;
    elseif (mod(t,4)==1)
        Vi(i,t) =  0.8 * cos(2*pi*fin1*(T*((i-1)*64+t)+ skew_mismatch(mod(t,4))));        
    else
       Vi(i,t) =  0.8 * cos(2*pi*fin1*(T*( (i-1) *64+t) + skew_mismatch(mod(t,4))-mismatch_1(i,mod(t,4))*step_size)) ;
    end
    Ao(i,t)=ADCF(Vi(i,t))-128;                           %非二进制ADC
    % Ao(i,t)=ADCF_2(Vi(i,t),8,0.9,0)*256-128;             %二进制ADC
    end
    A1=floor((Ao(i,4)*Ao(i,5))/s)  +floor((Ao(i,5)*Ao(i,6))/s)    +floor((Ao(i,6)*Ao(i,7))/s)+floor((Ao(i,7)*Ao(i,8))/s) ;  %互相关
    
    

    for t=2:4
      
           
              e(i,t)=-floor(Ao(i,t-1+4)*Ao(i,t+4)/s)*4;
            
            e(i,t)=floor((e(i,t)+A1)/h);
        mismatch(i+1,t)=mismatch(i,t)+u*e(i,t);
        mismatch_1(i+1,t)=floor(mismatch(i+1,t)/2^25);
    end
   
    

    
    Ao_64(i+1,1)=Ao(i,64);
end
%%%%%%%%%%%%%%%%%%%%%%%%%  未校准的图
Vi_2=zeros(N,1);
Ao_1=zeros(N,1);
for i = 1:N
    if(mod(i,4 )== 0)
        Vi_2(i) =  0.2 * cos(2*pi*fin1*(T*(i-1) + skew_mismatch(4))) +0.45;
    else
        Vi_2(i) = 0.2 * cos(2*pi*fin1*(T*(i-1) + skew_mismatch(mod(i,4))))+0.45 ;
    end
    %Ao_1(i)=ADCF(Vi_2(i))-128;                %非二进制ADC
    Ao_1(i)=ADCF_2(Vi_2(i),8,0.9,0)*256-128;    %二进制ADC
end


[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Ao_1),fs,8192,"校准前");
hold on

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%校准后的
Ao_2=zeros(N,1);

for i = 1:2^18-1
    for t=1:64
        Ao_2((i-1)*64+t,1)=Ao(i,t);
    end
end


[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Ao_2),fs,8192,"校准后");
hold on
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%不加误差
Vi_3=zeros(N,1);
Ao_3=zeros(N,1);
for i = 1:N
    if(mod(i,4 )== 0)
        Vi_3(i) =  0.2* cos(2*pi*fin1*(T*i))+0.45;
    else
        Vi_3(i) = 0.2 * cos(2*pi*fin1*(T*i))+0.45 ;
    end
    %Ao_3(i)=ADCF(Vi_3(i))-128; 
    Ao_3(i)=ADCF_2(Vi_3(i),8,0.9,0)*256-128;
end
[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Ao_3),fs,8192,"不加误差");
[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Vi_3),fs,8192,"原函数未进ADC");
hold on

figure(5);
for i=2:4
    
    plot(skew_mismatch(i)-mismatch_1(1:N/64-1,i)*step_size);
    xlabel('迭代次数')
    ylabel('time估计值')
    title([texlabel('time_skew收敛图')]);
    hold on
end
yline(0.5*10^-12);

%%%%%%%%%%%%%%%%%%%%%加10fs误差
Vi_4=zeros(N/64,64);

Vi_6=zeros(N,1);




%skew_mismatch_1=[0.5*10^-12,-0.01*10^-12,0.01*10^-12,-0.01*10^-12];
skew_mismatch_1=[0.5*10^-12,0.51*10^-12,0.49*10^-12,0.49*10^-12];
for i=1:N/64-1
    for t=1:64
        
    if(mod(t,4) == 0)
        Vi_4(i,t) =  0.2 * cos(2*pi*fin1*(T*((i-1)*64+t) + skew_mismatch_1(4))) +0.45;
    elseif (mod(t,4)~=1)
        Vi_4(i,t) =  0.2 * cos(2*pi*fin1*(T*( (i-1) *64+t) + skew_mismatch_1(mod(t,4))))+0.45 ;
    else
        Vi_4(i,t) =  0.2 * cos(2*pi*fin1*(T*((i-1)*64+t)+ skew_mismatch_1(mod(t,4))))+0.45;
    end
   % Ao(i,t)=ADCF(Vi(i,t))-128;                           %非二进制ADC
     Vi_6((i-1)*64+t,1)=ADCF_2(Vi_4(i,t),8,0.9,0)*256-128;             %二进制ADC
    end
end
[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Vi_6),fs,8192,"加10fs误差");


%%%%%%%%%%%%%%%%%%%%%直接用最后收敛的值与误差相减采样
Vi_7=zeros(N/64,64);

Vi_8=zeros(N,1);

for i=1:N/64-1
    for t=1:64
        
    if(mod(t,4) == 0)
        Vi_7(i,t) =  0.2 * cos(2*pi*fin1*(T*((i-1)*64+t) + skew_mismatch(4)-mismatch_1(250000,4)*step_size)) +0.45;
    elseif (mod(t,4)==1)
        Vi_7(i,t) =  0.2 * cos(2*pi*fin1*(T*((i-1)*64+t)+ skew_mismatch(1)))+0.45;        
    else
       Vi_7(i,t) =  0.2 * cos(2*pi*fin1*(T*( (i-1) *64+t) + skew_mismatch(mod(t,4))-mismatch_1(250000,mod(t,4))*step_size))+0.45 ;
    end
   % Ao(i,t)=ADCF(Vi(i,t))-128;                           %非二进制ADC
     Vi_8((i-1)*64+t,1)=ADCF_2(Vi_7(i,t),8,0.9,0)*256-128;             %二进制ADC
    end
end

[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Vi_8),fs,8192,"用收敛的值减去误差");
