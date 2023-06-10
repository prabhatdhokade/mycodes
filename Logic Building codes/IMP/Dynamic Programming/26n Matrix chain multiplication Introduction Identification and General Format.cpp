/* MCM format   

int solve(int arr[],int i,int j);

    if (i>j)
    return 0;
        for(int k =i;k<j;k++) {
            int temp ans = solve(arr,i,k) + solve(arr,k+1,j);

            ans = max(ans,temp ans) ;
        }
    return ans;

    }


*/