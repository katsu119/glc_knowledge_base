%ADC test

FS=1.8;
Vref=0.9;



y=(-FS:FS/100000:FS);
Vp=Vref/2+y/2;
Vn=Vref/2-y/2;
n=length(y);
x=1:1:n;
result=zeros(1,n);
error=zeros(1,n);

for i=1:1:n
    result(i)=(ADCF(y(i))-127.5)/128*FS;
    error(i)=y(i)-result(i);
end

figure(1)
plot(x,y)
hold on

plot(x,result)
hold on

figure(2)
plot(x,error)



