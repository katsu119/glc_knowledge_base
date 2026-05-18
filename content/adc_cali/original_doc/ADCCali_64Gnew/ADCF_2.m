function [out]=ADCF_2(in,n,FS,os)

%ADC behavior model
%design parameter => in:input to be sampled
%                      n: Quantified bit width
%                      FS:full scale ADC output
%                      os:ADC offset
%                      out:ADC quantified output


%defalut value
if(~exist('os','var'))
    os = 0;  % if not exist , assign zero
end

output=0;
N=length(in);
for j=1:N
    input=in(j);
    for i=1:n
        if (input>=FS/2^i-FS/2^(n+1))
            output=FS/2^(i)+output;
            input=input-FS/2^(i);
        end
    end
%     out(j)= output+FS/2^(n+1)+os;
    out(j)= output+os;
    output=0;
end
