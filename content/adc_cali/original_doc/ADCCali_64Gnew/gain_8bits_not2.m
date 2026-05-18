clc;
clear;
fs = 16*10^9;   %采样频率16GHz
T = 1/fs;       %采样间隔
fin1 = 22783/2^16*fs;  %输入正弦波频率
fin2 = 8131/65536*fs;
fin3 = 9413/65536*fs;
fin4 = 10111/65536*fs;
fin5 = 11137/65536*fs;
fin6 = 12239/65536*fs;
fin7 = 13477/65536*fs;
fin8 = 14379/65536*fs;
fin9 = 15479/65536*fs;
fin10 = 16573/65536*fs;
Tin = 1/(fin1);     %输入正弦波间隔 

N = 2^24;                    %采样点数
M = 16;                      %采样通道：16
t = 0:1/fs:(N-1)/fs;         %采样时刻

%%  generate random mismatch variable
skew_mismatch = zeros(1,M);
gain_mismatch = zeros(1,M);
offset_mismatch = zeros(1,M);
for i = 1:M     %generate random mismatch variable for each channel
    %skew_mismatch(i) = randn(1,1) * 0.01*T*8;
    gain_mismatch(i) = 1+randn(1,1) * 0.01;
    %offset_mismatch(i) = randn(1,1) * 0.01;
end
%skew_mismatch=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
offset_mismatch=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
%gain_mismatch=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1];
gain_mismatch=[1.02,1.031300148465590,0.954576539575034,0.986336265137245,0.991216938204290,1.020496433047322,0.965051238568253,1.011192478195326,0.974329693357975,1.040282349589059,1.021534902874259,0.984490723528908,0.975716693376054,0.967881100025152,1.031287431110972,0.991022806984492];
%40mv_offset
%offset_mismatch=[-0.0225884686100365,-0.0130768829630527,0.0357839693972576,0.0303492346633185,0.00714742903826096,0.0148969760778546,0.00671497133608081,0.0163023528916473,0.00726885133383238,-0.00787282803758638,-0.0106887045816803,0.0143838029281510,0.0137029854009523,-0.00241447041607358,-0.00864879917324457,0.00627707287528727];
%20mv_offset
%offset_mismatch=[0.00216855990585554,-0.0129542156382229,0.00200255861354737,0.00748091512289529,0.0152633943160118,-0.0136529392958583,0.00576532659383278,-0.00822004313859303,-0.00248219450326367,-0.00277537739812483,-0.0071452634256301,0.000369503804489841,-0.00267406198087474,0.000453181831691423,0.0102554853904953,-0.0177135464092140];

%% Before CAL
Vi=zeros(N,1);
Vi1=zeros(N,1);
Vi2=zeros(N,1);
j=200000;
Ao=zeros(j,M);
V_out=zeros(N,1);
offset_cal=zeros(1,M);
gamma=0.25;
beta=1/2^26; %control  the loop bandwidth 
F1=zeros(M,j);
F2=zeros(M,j);
F3=zeros(M,j);
F4=zeros(M,j);
%for i=1:M
%    F3(i,1)=0;
%end
step_size=0.05/31;   %控制字6位，调节范围为正负0.5
th=zeros(1,j);
th_fl=zeros(1,j);
int_limit=zeros(M,j);
Ao1=zeros(N,1);
Ao2=zeros(N,1);
Ao3=zeros(j,M);
w=2^-12;  %10HZ~10MHZ 10^-8~10^-2
for i = 1:j-1
    
    for r=1:M
        Vi1(16*(i-1)+r,1) =gain_mismatch(r)*0.4*cos(2*pi*fin1*(T*(16*(i-1)+r)))+0.45 + offset_mismatch(r);
%           Vi1(16*(i-1)+r,1) = offset_mismatch(r)+ (gain_mismatch(r)*0.4*cos(2*pi*fin1*(T*(16*(i-1)+r)))+0.45)/10+(gain_mismatch(r)*0.4*cos(2*pi*fin2*(T*(16*(i-1)+r)))+0.45)/10 ...
%          + (gain_mismatch(r)*0.4*cos(2*pi*fin3*(T*(16*(i-1)+r)))+0.45)/10+(gain_mismatch(r)*0.4*cos(2*pi*fin4*(T*(16*(i-1)+r)))+0.45)/10 ...
%         + (gain_mismatch(r)*0.4*cos(2*pi*fin5*(T*(16*(i-1)+r)))+0.45)/10+(gain_mismatch(r)*0.4*cos(2*pi*fin6*(T*(16*(i-1)+r)))+0.45)/10 ...
%           + (gain_mismatch(r)*0.4*cos(2*pi*fin7*(T*(16*(i-1)+r)))+0.45)/10+(gain_mismatch(r)*0.4*cos(2*pi*fin8*(T*(16*(i-1)+r)))+0.45)/10 ...
%           + (gain_mismatch(r)*0.4*cos(2*pi*fin9*(T*(16*(i-1)+r)))+0.45)/10+(gain_mismatch(r)*0.4*cos(2*pi*fin10*(T*(16*(i-1)+r)))+0.45)/10;
        Vi(16*(i-1)+r,1) =(1+F4(r,i)*step_size)*gain_mismatch(r)*0.4*cos(2*pi*fin1*(T*(16*(i-1)+r)))+0.45 + offset_mismatch(r);
%           Vi(16*(i-1)+r,1) = offset_mismatch(r)+ ((1+F4(r,i)*step_size)*gain_mismatch(r)*0.4*cos(2*pi*fin1*(T*(16*(i-1)+r)))+0.45)/10+((1+F4(r,i)*step_size)*gain_mismatch(r)*0.4*cos(2*pi*fin2*(T*(16*(i-1)+r)))+0.45)/10 ...
%           + ((1+F4(r,i)*step_size)*gain_mismatch(r)*0.4*cos(2*pi*fin3*(T*(16*(i-1)+r)))+0.45)/10+((1+F4(r,i)*step_size)*gain_mismatch(r)*0.4*cos(2*pi*fin4*(T*(16*(i-1)+r)))+0.45)/10 ...
%          + ((1+F4(r,i)*step_size)*gain_mismatch(r)*0.4*cos(2*pi*fin5*(T*(16*(i-1)+r)))+0.45)/10+((1+F4(r,i)*step_size)*gain_mismatch(r)*0.4*cos(2*pi*fin6*(T*(16*(i-1)+r)))+0.45)/10 ...
%           + ((1+F4(r,i)*step_size)*gain_mismatch(r)*0.4*cos(2*pi*fin7*(T*(16*(i-1)+r)))+0.45)/10+((1+F4(r,i)*step_size)*gain_mismatch(r)*0.4*cos(2*pi*fin8*(T*(16*(i-1)+r)))+0.45)/10 ...
%           + ((1+F4(r,i)*step_size)*gain_mismatch(r)*0.4*cos(2*pi*fin9*(T*(16*(i-1)+r)))+0.45)/10+((1+F4(r,i)*step_size)*gain_mismatch(r)*0.4*cos(2*pi*fin10*(T*(16*(i-1)+r)))+0.45)/10;
        
       Ao(i,r)=ADCF_2(Vi(16*(i-1)+r,1),8,0.9,0)*256-128;%int_limit(r,i);
       % Ao(i,r)=ADCF(Vi(16*(i-1)+r,1)/0.9,8,1,0)*1024-512-int_limit(r,i);%int_limit(r,i);
      
        V_out(16*(i-1)+r,1)=Ao(i,r);
        F1(r,i+1)=Ao(i,r)*Ao(i,r);
%  %     F2(r,i+1)=F1(r,i+1)+(1-gamma)*F2(r,i);
        th_fl(1,i)=round(th(1,i)/16);                %以平均作为参考时,但是有限制       
        F3(r,i+1)=F3(r,i)-beta*(F1(r,i+1)-th_fl(1,i));    %以平均作为参考时 
%        F3(r,i+1)=F3(r,i)-beta*(F1(r,i+1)-th(1,i));         %参考1通道时，th的迭代
       F4(r,i+1)=floor(F3(r,i+1)*512);         %以平均作为参考时
       th(1,i+1)=th(1,i+1)+F1(r,i+1);          %以平均作为参考时
%       if r==1                                         %参考1通道时，th的迭代
%           F4(r,i+1)=0;
%           th(1,i+1)=F1(r,i+1);
%       else
%           F4(r,i+1)=floor(F3(r,i+1)*512);%*256);
%       end
    end
end



figure;
for i=1:M
    plot(gain_mismatch(i)*(1+step_size*F4(i,1:j-50000)))
    hold on
end 

for i = 1:j-1
    for r=1:M
        
        Ao1(16*(i-1)+r,1)=ADCF_2(Vi1(16*(i-1)+r,1),8,0.9,0)*256-128;       
    end
end



[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(Ao1),fs,2^16,"增益失配校准前");
%ADC输出放大了4096倍
hold on

[SNR,SINAD,SFDR,ENOB]=ADC_dynamic_with_figure(rot90(V_out),fs,2^16,"增益失配校准后");
hold on 

