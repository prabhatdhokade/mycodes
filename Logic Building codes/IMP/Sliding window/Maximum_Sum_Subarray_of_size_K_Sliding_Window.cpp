#include<iostream>
#include<algorithm>
using namespace std;

//Maximum minimum Both


int main()
{
  int N;
  cin>>N;
  int input_arr[N];
  for(int i=0;i<N;i++)
  {
    cin>> input_arr[i];
  }
  int K;//blcok sizwe
  cin>>K;

  int i = 0;
  int j= 0;
  int MAX = 0;
  int MIN; 
  int sum = 0;

 // while (j < N)
  //{
    for(j = 0; j < N; j++)
    {   
        sum += input_arr[j];

         

        if(j - i + 1 == K) {
            
           
             MAX = max( sum, MAX );
             MIN = min( sum, MIN);
             sum -= input_arr[i];
             i++;

        }

    }
    
  //}
  cout<< MAX<<"\n"<<MIN;


}