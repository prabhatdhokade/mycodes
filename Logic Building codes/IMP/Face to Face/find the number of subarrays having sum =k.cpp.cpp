#include<bits/stdc++.h>

using namespace std;  

int main()             //this program contains  1 to N'th values (N= size of array)
{
    int n;
    cin>>n;
    int arr[n];
    for( int i =0; i< n; i++) {
        cin>>arr[i];
    }
    int k;
    cin>>k;




    int i =0,j=0;
    int sum =0 ;
    int count=0;

    while ( j< n) 
    {
        sum += arr[j];

        if ( sum < k) {
            j++;
        } 
        else if ( sum >= k) { 
            count++;
            sum -= arr[i];                    
            if ( sum >= k) {            // 12 123 23   
                count++;                // 12 2 23 3  123 
            }
            i++;
            j++;
        }
    }
    cout<<count;
}
