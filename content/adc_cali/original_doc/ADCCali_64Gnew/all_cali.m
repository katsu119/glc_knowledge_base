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
gain_mismatch = zeros(1,M);
offset_mismatch = zeros(1,M);
for i = 1:4     %generate random mismatch variable for each channel
    skew_mismatch(i) = randn(1,1) * 0.01*T*8;
    %gain_mismatch(i) = 1+randn(1,1) * 0.01;
    %offset_mismatch(i) = randn(1,1) * 0.01;
end

for i = 1:64     %generate random mismatch variable for each channel
    
    gain_mismatch(1,i) = 1+(rand(1,1)-0.5) * 0.1;
    offset_mismatch(1,i) = (rand(1,1)-0.5) * 0.05;
end
w=[2^-10,2^-11,2^-12,2^-13,2^-14,2^-15];  %10HZ~10MHZ 10^-8~10^-2
skew_mismatch=[0.5*10^-12,-1.7*10^-12,2.8*10^-12,-2.5*10^-12];
gain_step_size=0.05/31;
Vi=zeros(N/64,64);
Ao=zeros(N/64,64);
Ao_64=zeros(N/64,1);
mismatch=zeros(N/64-1,4);
mismatch_1=zeros(N/64-1,4);
e=zeros(N/64-1,4);
u=2^9;
%s=8;       %控制自相关后截尾的大小
s=16;
h=1;     %对sum没有截尾

time_step_size=1*10^-14;
beta=1/2^23;
Vi_1=zeros(N,1);

gain_f4=zeros(M,N/64-1);
gain_f3=zeros(M,N/64-1);
int_limit=zeros(M,N/64-1);
int=zeros(M,N/64-1);

gain_f1=zeros(M,N/64);
th_f1=zeros(1,N/64);
th=zeros(1,N/64);

for i=1:N/64-1
    for t=1:64
        
    if(mod(t,4) == 0)
        Vi(i,t) =  (1+gain_f4(t,i)*gain_step_size)*gain_mismatch(1,t)*0.8* cos(2*pi*fin1*(T*((i-1)*64+t) + skew_mismatch(4)-mismatch_1(i,4)*time_step_size))+ offset_mismatch(1,t)-int_limit(t,i)/256 ;
    elseif (mod(t,4)==1)
        Vi(i,t) =  (1+gain_f4(t,i)*gain_step_size)*gain_mismatch(1,t)*0.8* cos(2*pi*fin1*(T*((i-1)*64+t)+ skew_mismatch(mod(t,4))))+ offset_mismatch(1,t)-int_limit(t,i)/256;        
    else
       Vi(i,t) =  (1+gain_f4(t,i)*gain_step_size)*gain_mismatch(1,t)*0.8* cos(2*pi*fin1*(T*( (i-1) *64+t) + skew_mismatch(mod(t,4))-mismatch_1(i,mod(t,4))*time_step_size))+ offset_mismatch(1,t)-int_limit(t,i)/256 ;
    end
    Ao(i,t)=ADCF(Vi(i,t))-128;                           %非二进制ADC
     %Ao(i,t)=ADCF_2(Vi(i,t),8,0.9,0)*256-128;             %二进制ADC
    %%%%%%%%%%%%%%%%gain校准部分
     gain_f1(t,i+1)=Ao(i,t)*Ao(i,t);
     th_fl(1,i)=round(th(1,i)/64);
     gain_f3(t,i+1)=gain_f3(t,i)-beta*(gain_f1(t,i+1)-th_fl(1,i));
     gain_f4(t,i+1)=floor(gain_f3(t,i+1)*512);
     th(1,i+1)=th(1,i+1)+gain_f1(t,i+1);

    

     %%%%%%%%%%%%%%%offset校准部分
      int(t,i+1)=int(t,i)+w(1)*Ao(i,t);
      int_limit(t,i+1)=floor(int(t,i+1)*4)/4;%小数点后只有两位  




    end
    A1=floor((Ao_64(i,1)* Ao(i,1))/s)     + floor((Ao(i,1)*Ao(i,2))/s)  +floor((Ao(i,2)*Ao(i,3))/s)    +floor((Ao(i,3)*Ao(i,4))/s);  %互相关
    A2= floor((Ao(i,4)*Ao(i,5))/s)       +floor((Ao(i,5)*Ao(i,6))/s)    +floor((Ao(i,6)*Ao(i,7))/s)    +floor((Ao(i,7)*Ao(i,8))/s);
    A3= floor((Ao(i,8)*Ao(i,9))/s)       +floor((Ao(i,9)*Ao(i,10))/s)   +floor((Ao(i,10)*Ao(i,11))/s)  +floor((Ao(i,11)*Ao(i,12))/s);
    A4= floor((Ao(i,12)*Ao(i,13))/s)     +floor((Ao(i,13)*Ao(i,14))/s)  +floor((Ao(i,14)*Ao(i,15))/s)  +floor((Ao(i,15)*Ao(i,16))/s);
    A5=floor(( Ao(i,16)*Ao(i,17))/s)    +floor((Ao(i,17)*Ao(i,18))/s)   +floor((Ao(i,18)*Ao(i,19))/s)  +floor((Ao(i,19)*Ao(i,20))/s);
    A6= floor((Ao(i,20)*Ao(i,21))/s)    +floor((Ao(i,21)*Ao(i,22))/s)   +floor((Ao(i,22)*Ao(i,23))/s)  +floor((Ao(i,23)*Ao(i,24))/s);
    A7= floor((Ao(i,24)*Ao(i,25))/s)    +floor((Ao(i,25)*Ao(i,26))/s)   +floor((Ao(i,26)*Ao(i,27))/s)  +floor((Ao(i,27)*Ao(i,28))/s);
    A8= floor((Ao(i,28)*Ao(i,29))/s)    +floor((Ao(i,29)*Ao(i,30))/s)   +floor((Ao(i,30)*Ao(i,31))/s)  +floor((Ao(i,31)*Ao(i,32))/s);
    A9=floor(( Ao(i,32)*Ao(i,33))/s)    +floor((Ao(i,33)*Ao(i,34))/s)   +floor((Ao(i,34)*Ao(i,35))/s)  +floor((Ao(i,35)*Ao(i,36))/s);
    A10=floor(( Ao(i,36)*Ao(i,37))/s)   +floor((Ao(i,37)*Ao(i,38))/s)   +floor((Ao(i,38)*Ao(i,39))/s)  +floor((Ao(i,39)*Ao(i,40))/s);
    A11= floor((Ao(i,40)*Ao(i,41))/s)   +floor((Ao(i,41)*Ao(i,42))/s)   +floor((Ao(i,42)*Ao(i,43))/s)  +floor((Ao(i,43)*Ao(i,44))/s);
    A12= floor((Ao(i,44)*Ao(i,45))/s)   +floor((Ao(i,45)*Ao(i,46))/s)   +floor((Ao(i,46)*Ao(i,47))/s)  +floor((Ao(i,47)*Ao(i,48))/s);
    A13=floor(( Ao(i,48)*Ao(i,49))/s)   +floor((Ao(i,49)*Ao(i,50))/s)   +floor((Ao(i,50)*Ao(i,51))/s)  +floor((Ao(i,51)*Ao(i,52))/s);
    A14=floor(( Ao(i,52)*Ao(i,53))/s)   +floor((Ao(i,53)*Ao(i,54))/s)   +floor((Ao(i,54)*Ao(i,55))/s)  +floor((Ao(i,55)*Ao(i,56))/s);
    A15= floor((Ao(i,56)*Ao(i,57))/s)   +floor((Ao(i,57)*Ao(i,58))/s)   +floor((Ao(i,58)*Ao(i,59))/s)  +floor((Ao(i,59)*Ao(i,60))/s);
    A16=floor(( Ao(i,60)*Ao(i,61))/s)   +floor((Ao(i,61)*Ao(i,62))/s)   +floor((Ao(i,62)*Ao(i,63))/s)  +floor((Ao(i,63)*Ao(i,64))/s);
    A17=A1+A2+A3+A4+A5+A6+A7+A8+A9+A10+A11+A12+A13+A14+A15+A16;

    for t=2:4
      
            for m=1:16
              e(i,t)=-floor(Ao(i,t-1+(m-1)*4)*Ao(i,t+(m-1)*4)/s)*4+e(i,t);
            end
            e(i,t)=floor((e(i,t)+A17)/h);
        mismatch(i+1,t)=mismatch(i,t)+u*e(i,t);
        mismatch_1(i+1,t)=floor(mismatch(i+1,t)/2^24);
    end
   
    

    
    Ao_64(i+1,1)=Ao(i,64);
end
%%%%%%%%%%%%%%%%%%%%%%%%%  未校准的图
Vi_2=zeros(N/64,64);
Ao_1=zeros(N,1);
for i=1:N/64-1
    for t=1:64
        
    if(mod(t,4) == 0)
        Vi_2(i,t) =  gain_mismatch(1,t)*0.8* cos(2*pi*fin1*(T*((i-1)*64+t) + skew_mismatch(4)))+ offset_mismatch(1,t) ;
    elseif (mod(t,4)==1)
        Vi_2(i,t) =  gain_mismatch(1,t)*0.8* cos(2*pi*fin1*(T*((i-1)*64+t)+ skew_mismatch(mod(t,4))))+ offset_mismatch(1,t);        
    else
       Vi_2(i,t) =  gain_mismatch(1,t)*0.8* cos(2*pi*fin1*(T*( (i-1) *64+t) + skew_mismatch(mod(t,4))))+ offset_mismatch(1,t) ;
    end
    Ao_1((i-1)*64+t)=ADCF(Vi_2(i,t))-128;                %非二进制ADC
    %Ao_1(i)=ADCF_2(Vi_2(i),8,0.9,0)*256-128;    %二进制ADC
    end
end


[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Ao_1),fs,8192,"before calibration");
hold on

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%校准后的
Ao_2=zeros(N,1);

for i = 1:2^18-1
    for t=1:64
        Ao_2((i-1)*64+t,1)=Ao(i,t);
    end
end


[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Ao_2),fs,8192,"after calibration");
hold on
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%不加误差
% Vi_3=zeros(N,1);
% Ao_3=zeros(N,1);
% for i = 1:N
%     if(mod(i,4 )== 0)
%         Vi_3(i) =  0.2* cos(2*pi*fin1*(T*i))+0.45;
%     else
%         Vi_3(i) = 0.2 * cos(2*pi*fin1*(T*i))+0.45 ;
%     end
%     %Ao_3(i)=ADCF(Vi_3(i))-128; 
%     Ao_3(i)=ADCF_2(Vi_3(i),8,0.9,0)*256-128;
% end
% [SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Ao_3),fs,8192,"不加误差");
% [SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Vi_3),fs,8192,"原函数未进ADC");
% hold on

figure(5);
for i=2:4
    
    plot(skew_mismatch(i)-mismatch_1(1:N/64-1,i)*time_step_size);
    xlabel('迭代次数')
    ylabel('time估计值')
    title([texlabel('time_skew收敛图')]);
    hold on
end
yline(0.5*10^-12);

% %%%%%%%%%%%%%%%%%%%%%加10fs误差
% Vi_4=zeros(N/64,64);
% 
% Vi_6=zeros(N,1);
% 
% 
% 
% 
% %skew_mismatch_1=[0.5*10^-12,-0.01*10^-12,0.01*10^-12,-0.01*10^-12];
% skew_mismatch_1=[0.5*10^-12,0.51*10^-12,0.49*10^-12,0.49*10^-12];
% for i=1:N/64-1
%     for t=1:64
%         
%     if(mod(t,4) == 0)
%         Vi_4(i,t) =  0.2 * cos(2*pi*fin1*(T*((i-1)*64+t) + skew_mismatch_1(4))) +0.45;
%     elseif (mod(t,4)~=1)
%         Vi_4(i,t) =  0.2 * cos(2*pi*fin1*(T*( (i-1) *64+t) + skew_mismatch_1(mod(t,4))))+0.45 ;
%     else
%         Vi_4(i,t) =  0.2 * cos(2*pi*fin1*(T*((i-1)*64+t)+ skew_mismatch_1(mod(t,4))))+0.45;
%     end
%    % Ao(i,t)=ADCF(Vi(i,t))-128;                           %非二进制ADC
%      Vi_6((i-1)*64+t,1)=ADCF_2(Vi_4(i,t),8,0.9,0)*256-128;             %二进制ADC
%     end
% end
% [SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Vi_6),fs,8192,"加10fs误差");


% %%直接用最后收敛的值与误差相减采样
% Vi_7=zeros(N/64,64);
% 
% Vi_8=zeros(N,1);
% 
% for i=1:N/64-1
%     for t=1:64
%         
%     if(mod(t,4) == 0)
%         Vi_7(i,t) =  0.2 * cos(2*pi*fin1*(T*((i-1)*64+t) + skew_mismatch(4)-mismatch_1(250000,4)*time_step_size)) +0.45;
%     elseif (mod(t,4)==1)
%         Vi_7(i,t) =  0.2 * cos(2*pi*fin1*(T*((i-1)*64+t)+ skew_mismatch(1)))+0.45;        
%     else
%        Vi_7(i,t) =  0.2 * cos(2*pi*fin1*(T*( (i-1) *64+t) + skew_mismatch(mod(t,4))-mismatch_1(250000,mod(t,4))*time_step_size))+0.45 ;
%     end
%    % Ao(i,t)=ADCF(Vi(i,t))-128;                           %非二进制ADC
%      Vi_8((i-1)*64+t,1)=ADCF_2(Vi_7(i,t),8,0.9,0)*256-128;             %二进制ADC
%     end
% end
% 
% [SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Vi_8),fs,8192,"用收敛的值减去误差");