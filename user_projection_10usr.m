function [H_proj, sp_gain, theta] = user_projection_10usr(H,  nVar, n_sta, n_ap, numTx, assigned_idxs)
    
    Hcov_matrx = H*H'; 
    noise_diag = nVar*eye(n_ap,n_ap);
    Hcov_matrxN = Hcov_matrx + noise_diag;
    invH =  inv(Hcov_matrxN); 
    csi = 1./abs(diag(invH));

    [warnmsg, msgid] = lastwarn;
        sp_gain = zeros(n_sta,1);
        H_proj = ((invH)*H)';
        
        % Estimate the spatial gain for the assignment
        for s=1:numTx 
            hproj = H_proj(s,:);
            %hproj = reshape(hproj, 1,n_ap);
            usrH = H(:,s); 

            dotH = abs(hproj*usrH);
            length1 = norm(hproj);
            length2 = norm(usrH);
            sp_gain((assigned_idxs(s)),:) = dotH/(length1*length2);
            
            ang_r = acos((dotH/(length1*length2)) );
            ang_deg = ang_r*(180/pi);
            theta((assigned_idxs(s)),:) = ang_deg;
            
        end
%         warning('off','all');
    %end
    warning('off','all');
end