function [SINR, rate, nullsp_gain, ulPow] = marl_ul_env_opt_2(chnSnr_data, action)
% % function [SINR, rate, rateU, nullsp_gain, nullsp_gainU] = marl_ul_env(chnSnr_data, n_sta, n_ap, n_ru, ulPow, ulPowU)
%% Paramters
B = 20e6; % bandwidth
n_ru = 9;
n_sta = 10;
n_ap = 4;
n_apO= 4;
%% Rate region - approximation by lines
a = [0.1067 0.0536 0.0457 0.0339 0.0170 0.0170 0.0085 0.0021 0.0018 0.0013 0.0008 0.0007 0];
b = [0 0.1679 0.2177 0.3359 0.6734 0.6718 1.3468 2.3609 2.4605 2.6968 3.2806 3.3696 5.6250];
users_chn_echRUO = (n_apO*n_sta);
users_chn_echRU = (n_ap*n_sta);
users_noise_echRU = (n_ap*n_sta)*n_ru;

nullsp_gain = zeros(n_sta,n_ru);
SINR = zeros(n_sta,n_ru);

rate = zeros(n_sta,n_ru);
ulPow = zeros(n_sta,n_ru);

noise_echRU = zeros(1,n_ru);
P_total = 9*10;
%UL power allocation and SNR estimation for rate calculation------------------------------------------    

    for sc = 1:n_ru
        H_mat= [];
        noise = [];
        pow = [];
        for u = 1:n_sta

            if sum(action(u,:)) >0
                if sc == 1
                    ulPow(u, (action(u,:)>0)) = P_total/sum(action(u,:));
                end
                if ulPow(u,sc) >0
                    usrData = chnSnr_data(:, ((sc-1)*users_chn_echRU)+1: (sc*users_chn_echRU) );
                    H_mat = [H_mat reshape(usrData(1,(((u-1)*n_ap)+1):(u*n_ap)), n_ap,1) ];   
                    noise = [noise chnSnr_data(:, (users_noise_echRU+((u-1)*n_ap)+1 ) )];
                    pow = [pow ulPow(u,sc)];
                end

            end


        end
        
        if sum(action(:,sc)) >0
            actions = action(:,sc)';
            numTx = sum(actions);
            assigned_idxs = zeros(1,numTx);
            [vals,idx] = sort(actions);
            assigned_idxs = idx(:,(end-numTx+1):end);
            
            % SINR, rate for selected users------------------------------
            if (numTx > 1)
                noiseVar =  mean((numTx*(B/n_ru))*(noise)); %mean( (asgnd_ru*(B/n_ru))*noiseEst );

                P = pow.*eye(numTx, numTx);
                n = noiseVar*eye(n_ap,n_ap);
                G = H_mat*P;

                [W, sp_gain, theta] = user_projection_10usr(G,  noiseVar, n_sta, n_ap, numTx, assigned_idxs);

                nullsp_gain(:,sc) = sp_gain;

                for k = 1:numTx
                    wkH = W(k,:);
                    gk = G(:,k);
                    Gk = [];
                    if k ==1
                        Gk = G(:, (k+1):end);
                    elseif k == numTx
                        Gk = G(:, 1:(numTx-1));
                    else
                        Gk = [G(:,1:(k-1)) G(:,(k+1):end)];
                    end

                    numer = (abs(wkH*gk)^2);
                    denom = wkH*( (Gk*Gk') + n )*wkH';
                    SINR(assigned_idxs(k),sc) = numer/real(denom);
                    SINR_db = -10*log10(SINR(assigned_idxs(k),sc));

                    mcs = round(abs(SINR_db)/3);
                    if mcs == 0 || mcs < 0 || SINR_db > -4
                       rate(assigned_idxs(k),sc) = 0;
%                        nullsp_gain(assigned_idxs(k),sc) = 0;
                    elseif mcs > 13
                        mcs = 13;
                        rate(assigned_idxs(k),sc) = (a(:,mcs)*SINR(assigned_idxs(k),sc) + b(:,mcs));
                    else
                        rate(assigned_idxs(k),sc) = (a(:,mcs)*SINR(assigned_idxs(k),sc) + b(:,mcs));
                    end
                end

            elseif (numTx == 1)
                noiseVar = mean((numTx*(B/n_ru))*(noise));
                nullsp_gain(assigned_idxs(1), sc) = 1;
                H_single = ulPow(assigned_idxs(1), sc).*H_mat;
                SINR(assigned_idxs(1),sc) = (norm(H_single)^2)/noiseVar;
                SINR_db = -10*log10(SINR(assigned_idxs(1),sc));

                mcs = round(abs(SINR_db)/3);
                if mcs == 0 || mcs < 0 || SINR_db > -4
                   rate(assigned_idxs(1),sc) = 0;
%                    nullsp_gain(assigned_idxs(1),sc) = 0;
                elseif mcs > 13
                    mcs = 13;
                    rate(assigned_idxs(1),sc) = (a(:,mcs)*SINR(assigned_idxs(1),sc) + b(:,mcs));
                else
                    rate(assigned_idxs(1),sc) = (a(:,mcs)*SINR(assigned_idxs(1),sc) + b(:,mcs));
                end

            else
                nullsp_gain(:,sc) = 0;
            end

        end    
        

    end

end