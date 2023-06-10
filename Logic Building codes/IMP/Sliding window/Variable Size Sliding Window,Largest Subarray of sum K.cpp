//input : 
// 7
//4 1 1 1 2 3 5
//5
//output : 4 
#include<bits/stdc++.h>

using namespace std;

int main()
{
  int n;
  cin>>n;
  int arr[n];
  for(int i=0;i<n;i++)
    {
        cin>> arr[i];
    }
  int k; // here we take it as sum 
  cin>>k;


  int i,j,maxi=0;
  i=j=0;
  int sum=0;

  while(j< n) 
   {
        sum += arr[j];

        if( k > sum) {
            j++;
        }

        else if ( k == sum) { 
            maxi =max(maxi, j-i+1); // we'll get max subarry from here
            j++;
        }

        else if (k < sum) { // if the sum value becomes greater than k then
            while (sum > k) {
                sum -= arr[i];
                i++;
            } 
            if ( sum == k) {  // after the i++ if the k value equals to sum then we have do the foll step 
                maxi = max(maxi,j-i+1);
                j++;
            }
            j++;
        } 
    }
    cout<<maxi;
}