function [out]=ADCF_Binary(inp,inn)

%ADC behavior model
%



%defalut value

Vp=inp;
Vn=inn;
s=zeros(1,8);
Vn=Vn/0.9*128;
Vp=Vp/0.9*128;
r=[64,32,16,8,4,2,1,1/2];
if Vp>=Vn
    s(1,1)=1;
else
    s(1,1)=0;
end

for i=1:5
    if s(1,i)==1
        Vp=Vp-r(i+1);
        Vn=Vn+r(i+1);
    else
        Vp=Vp+r(i+1);
        Vn=Vn-r(i+1);
    end
    if Vp>=Vn
    s(1,i+1)=1;
    else
    s(1,i+1)=0;
    end
end

if  s(6)==1
    Vp=Vp-r(7);
    Vn=Vn+r(7);
else 
    Vp=Vp+r(7);
    Vn=Vn-r(7);
end

if Vp>Vn
   s(7)=1;
   Vp=Vp-r(8);
else
   s(7)=0;
   Vn=Vn-r(8);
end

if Vp>Vn
    s(8)=1;
else
    s(8)=0;
end


out=s(1,1)*128+s(1,2)*64+s(1,3)*32+s(1,4)*16+s(1,5)*8+s(1,6)*4+s(1,7)*2+s(1,8)*1;




